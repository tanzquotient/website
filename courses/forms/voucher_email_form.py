from django import forms
from django.utils.translation import gettext_lazy as _


class VoucherEmailForm(forms.Form):
    custom_email_message_en = forms.CharField(
        max_length=200,
        label=_("Custom message (English)."),
    )
    custom_email_message_de = forms.CharField(
        max_length=200,
        label=_("Custom message (German)."),
    )
