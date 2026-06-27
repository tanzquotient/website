import logging

from django.http import HttpRequest, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from courses.models import Subscribe
from payment.models import PayrexxGateway
from payment.services.payrexx import create_gateway

log = logging.getLogger(__name__)

VALID_METHODS = {PayrexxGateway.METHOD_CARD, PayrexxGateway.METHOD_TWINT}


def payrexx_gateway_view(request: HttpRequest, usi: str, method: str):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    if method not in VALID_METHODS:
        return HttpResponseBadRequest(f"Invalid payment method: {method!r}")

    subscription = get_object_or_404(Subscribe, usi=usi)

    if not subscription.course.payrexx_enabled:
        return HttpResponseBadRequest(
            "Payrexx payments are not enabled for this course."
        )

    if not subscription.open_amount() > 0:
        return HttpResponseBadRequest("No outstanding balance.")

    # Reuse an existing pending gateway to prevent double-charging the user
    existing = (
        PayrexxGateway.objects.filter(
            subscription=subscription,
            payment_method=method,
            status=PayrexxGateway.PENDING,
        )
        .order_by("-created_at")
        .first()
    )
    if existing:
        log.info(
            "Reusing existing pending Payrexx gateway %s for subscription %s",
            existing.gateway_id,
            usi,
        )
        return redirect(existing.link)

    payment_page_url = request.build_absolute_uri(
        reverse("payment:subscription_payment", args=[usi])
    )

    link, gateway_id, gross = create_gateway(
        subscription,
        method,
        success_url=payment_page_url,
        cancel_url=payment_page_url,
    )

    PayrexxGateway.objects.create(
        subscription=subscription,
        payment_method=method,
        gateway_id=gateway_id,
        link=link,
        gross_amount=gross,
        status=PayrexxGateway.PENDING,
    )
    log.info(
        "Created Payrexx gateway %s for subscription %s (%s)", gateway_id, usi, method
    )
    return redirect(link)
