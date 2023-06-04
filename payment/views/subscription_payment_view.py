from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render

from courses.models import Subscribe, Voucher
from email_system.services import send_email
from payment.forms import VoucherForm
from tq_website import settings


def subscription_payment_view(request: HttpRequest, usi: str):
    subscription = get_object_or_404(Subscribe, usi=usi)

    # Get form
    voucher_form_date = request.POST if request.method == "POST" else None
    voucher_form = VoucherForm(data=voucher_form_date)

    # In case there is a remainder after applying the voucher
    voucher_for_remainder = None
    voucher_applied = False

    # Apply voucher
    if voucher_form.is_valid():
        voucher = Voucher.objects.get(key=voucher_form.cleaned_data["voucher_code"])
        _, voucher_for_remainder = voucher.apply_to(subscription)
        voucher_applied = True
        voucher_form = VoucherForm()

    if voucher_for_remainder:
        email_context = {
            "first_name": subscription.user.first_name,
            "last_name": subscription.user.last_name,
            "voucher_key": voucher_for_remainder.key,
            "voucher_url": voucher_for_remainder.pdf_file.url,
        }
        send_email(
            to=subscription.user.email,
            template="voucher",
            context=email_context,
            attachments={"Voucher.pdf": voucher_for_remainder.pdf_file.file},
        )

    context = dict(
        subscription=subscription,
        voucher_form=voucher_form,
        voucher_for_remainder=voucher_for_remainder,
        voucher_applied=voucher_applied,
        payment_account=settings.PAYMENT_ACCOUNT["default"],
    )

    return render(request, "payment/subscription/index.html", context)
