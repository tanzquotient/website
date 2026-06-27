import datetime

from django import forms
from django.forms.widgets import SelectDateWidget
from django.utils.translation import gettext_lazy as _

from ..models import Voucher, VoucherPurpose
from ..utils import validate_amount


class VoucherForm(forms.Form):
    amount = forms.IntegerField(label=_("Value of the voucher in CHF."))
    purpose = forms.ModelChoiceField(queryset=VoucherPurpose.objects)
    expires_flag = forms.BooleanField(
        label=_("Set expire date?"), initial=True, required=False
    )
    expires = forms.DateField(
        widget=SelectDateWidget,
        initial=lambda: datetime.date.today().replace(
            year=datetime.date.today().year + 5
        ),
    )
    custom_email_message_en = forms.CharField(
        required=False,
        max_length=200,
        label=_("Custom message (English)."),
    )
    custom_email_message_de = forms.CharField(
        required=False,
        max_length=200,
        label=_("Custom message (German)."),
    )
    voucher_comment = forms.CharField(
        required=False,
        max_length=Voucher._meta.get_field("comment").max_length,
        label=_("Internal comment for the voucher."),
    )

    def clean_amount(self) -> int:
        return validate_amount(self.cleaned_data)
