from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .voucher_form import VoucherForm


class CreateSendVoucherForm(VoucherForm):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    amount = forms.IntegerField(label=_("Value of the voucher in CHF."), required=False)
    percentage = forms.IntegerField(
        label=_("Reduction in percent (0-100)."), required=False
    )

    def clean(self) -> dict:
        cleaned_data = super().clean()
        amount = cleaned_data.get("amount")
        percentage = cleaned_data.get("percentage")
        if not amount and not percentage:
            raise ValidationError("Set either an amount or a percentage.")
        if amount and percentage:
            raise ValidationError("Set either an amount or a percentage, not both.")
        return cleaned_data

    def clean_percentage(self) -> int:
        percentage = self.cleaned_data.get("percentage")
        if percentage is not None and (percentage < 0 or percentage > 100):
            raise ValidationError("Percentage must be between 0 and 100.")
        return percentage
