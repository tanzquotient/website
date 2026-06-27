"""
Payrexx webhook handler.

Payrexx POSTs a JSON payload to this endpoint when a transaction status changes.
We verify the signature, then on 'confirmed' status: create a Payment +
SubscriptionPayment record and mark the subscription as paid.

Payrexx retries delivery up to 10 times with escalating backoff; idempotency is
enforced via the unique payrexx_transaction_id field on PayrexxGateway.
"""

import json
import logging

from django.http import HttpRequest, HttpResponse
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from courses.models import Subscribe
from courses.models.choices import PaymentMethod, SubscribeState
from payment.models import Payment, PayrexxGateway, SubscriptionPayment
from payment.models.choices import CreditDebit, State, Type
from payment.services.payrexx import verify_webhook_signature

log = logging.getLogger(__name__)

_TERMINAL_STATUSES = {
    "confirmed",
    "cancelled",
    "declined",
    "failed",
    "expired",
    "error",
    "chargeback",
    "refunded",
    "partially-refunded",
}


@csrf_exempt
@require_POST
def payrexx_webhook_view(request: HttpRequest) -> HttpResponse:
    body = request.body
    signature = request.headers.get("X-Webhook-Signature", "")

    if not verify_webhook_signature(body, signature):
        log.warning("Payrexx webhook: invalid signature")
        return HttpResponse(status=400)

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        log.warning("Payrexx webhook: malformed JSON")
        return HttpResponse(status=400)

    # Payrexx wraps transaction data in a list under "transaction"
    transaction = payload.get("transaction") or payload.get("Transaction")
    if not transaction:
        log.info("Payrexx webhook: no transaction object, ignoring")
        return HttpResponse(status=200)

    status = transaction.get("status", "")
    transaction_id = transaction.get("id")
    reference_id = (transaction.get("invoice") or {}).get(
        "referenceId"
    ) or transaction.get("referenceId", "")
    amount_cents = transaction.get("amount", 0)

    log.info(
        "Payrexx webhook: transaction_id=%s status=%s referenceId=%s",
        transaction_id,
        status,
        reference_id,
    )

    if status not in _TERMINAL_STATUSES:
        # Non-terminal status (e.g. "waiting") — acknowledge and do nothing
        return HttpResponse(status=200)

    # Update gateway status for all non-confirmed terminal states
    if status != "confirmed":
        PayrexxGateway.objects.filter(
            gateway_id=transaction.get("paymentLinkId")
        ).update(status=status)
        return HttpResponse(status=200)

    # --- Payment confirmed ---

    # Idempotency: skip if this transaction was already processed
    if PayrexxGateway.objects.filter(payrexx_transaction_id=transaction_id).exists():
        log.info(
            "Payrexx webhook: transaction %s already processed, skipping",
            transaction_id,
        )
        return HttpResponse(status=200)

    # Resolve subscription
    try:
        subscription = Subscribe.objects.get(usi=reference_id)
    except Subscribe.DoesNotExist:
        log.error(
            "Payrexx webhook: no subscription found for referenceId=%r (transaction %s)",
            reference_id,
            transaction_id,
        )
        return HttpResponse(status=200)

    # Parse timestamp
    raw_time = transaction.get("time", "")
    payment_date = parse_datetime(raw_time) if raw_time else None
    if payment_date is None:
        from django.utils import timezone

        payment_date = timezone.now()
    elif payment_date.tzinfo is None:
        payment_date = make_aware(payment_date)

    gross_amount = amount_cents / 100  # cents → CHF

    # Determine payment method from gateway record (if available)
    gateway = (
        PayrexxGateway.objects.filter(
            payrexx_transaction_id__isnull=True,
            subscription=subscription,
            status=PayrexxGateway.PENDING,
        )
        .order_by("-created_at")
        .first()
    )

    payment_method = PaymentMethod.CARD
    if gateway and gateway.payment_method == PayrexxGateway.METHOD_TWINT:
        payment_method = PaymentMethod.TWINT

    # Create Payment record (audit trail / finance reporting)
    net_amount = subscription.open_amount()
    payment = Payment.objects.create(
        transaction_id=str(transaction_id),
        amount=gross_amount,
        currency_code="CHF",
        date=payment_date,
        state=State.PROCESSED,
        type=Type.SUBSCRIPTION_PAYMENT,
        credit_debit=CreditDebit.CREDIT,
        remittance_user_string=f"payrexx-{reference_id}",
        name=f"{subscription.user.first_name} {subscription.user.last_name}",
        filename="",
    )

    # Link payment to subscription (net amount settles the open balance)
    SubscriptionPayment.objects.create(
        payment=payment,
        subscription=subscription,
        amount=net_amount,
    )

    # Mark gateway as completed
    if gateway:
        gateway.status = PayrexxGateway.COMPLETED
        gateway.payrexx_transaction_id = transaction_id
        gateway.payment = payment
        gateway.save(update_fields=["status", "payrexx_transaction_id", "payment"])
    else:
        # No matching gateway found (e.g. gateway was manually deleted); update by gateway_id
        PayrexxGateway.objects.filter(
            gateway_id=transaction.get("paymentLinkId")
        ).update(
            status=PayrexxGateway.COMPLETED,
            payrexx_transaction_id=transaction_id,
            payment=payment,
        )

    # Transition subscription to paid
    if subscription.state == SubscribeState.CONFIRMED:
        subscription.mark_as_paid(payment_method)
        log.info(
            "Subscription %s marked as paid via Payrexx (%s, transaction %s)",
            reference_id,
            payment_method,
            transaction_id,
        )
    else:
        log.warning(
            "Payrexx webhook: subscription %s in state %r — not marking as paid (transaction %s)",
            reference_id,
            subscription.state,
            transaction_id,
        )

    return HttpResponse(status=200)
