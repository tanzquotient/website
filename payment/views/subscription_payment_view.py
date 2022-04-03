from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render

from courses.models import Subscribe, Voucher
from payment.forms import VoucherForm
from tq_website import settings


def subscription_payment_view(request: HttpRequest, usi: str):
    subscription = get_object_or_404(Subscribe, usi=usi)

    # Get form
    voucher_form_date = request.POST if request.method == 'POST' else None
    voucher_form = VoucherForm(data=voucher_form_date)

    # In case there is a remainder after applying the voucher
    voucher_for_remainder = None

    # Apply voucher
    if voucher_form.is_valid():
        voucher = Voucher.objects.get(key=voucher_form.cleaned_data['voucher_code'])
        _, voucher_for_remainder = voucher.apply_to(subscription)
        voucher_form = VoucherForm()

    context = dict(
        subscription=subscription,
        voucher_form=voucher_form,
        voucher_for_remainder=voucher_for_remainder,
        payment_account=settings.PAYMENT_ACCOUNT['default']
    )

    return render(request, "payment/subscription/index.html", context)
