from django import forms
from django.utils.translation import gettext as _

from . import VoucherForm


class VoucherGenerationForm(VoucherForm):
    number_of_vouchers = forms.IntegerField(
        label=_("How many voucher should be generated?"), initial=20
    )
