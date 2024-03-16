import datetime

from django import forms
from django.forms import ValidationError
from django.forms.widgets import SelectDateWidget
from django.utils.translation import gettext_lazy as _

from ..models import VoucherPurpose
from ..utils import validate_amount_and_percentage, validate_amount, validate_percentage


class VoucherForm(forms.Form):
    percentage = forms.IntegerField(
        label=_("Reduction in percent (0-100)."), required=False
    )
    amount = forms.IntegerField(label=_("Value of the voucher in CHF."), required=False)
    purpose = forms.ModelChoiceField(queryset=VoucherPurpose.objects)
    expires_flag = forms.BooleanField(
        label=_("Set expire date?"), initial=False, required=False
    )
    expires = forms.DateField(
        widget=SelectDateWidget,
        initial=datetime.date.today() + datetime.timedelta(days=365),
    )
    custom_email_message_en = forms.CharField(
        max_length=200,
        label=_("Custom message to add at the beginning of the email (English).")
    )
    custom_email_message_de = forms.CharField(
        max_length=200,
        label=_("Custom message to add at the beginning of the email (German).")
    )

    def clean(self) -> dict:
        cleaned_data = super().clean()
        return validate_amount_and_percentage(cleaned_data)

    def clean_amount(self) -> int:
        return validate_amount(self.cleaned_data)

    def clean_percentage(self) -> int:
        return validate_percentage(self.cleaned_data)
