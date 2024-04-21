from django import forms

from . import VoucherEmailForm


class SendVoucherEmailForm(VoucherEmailForm):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
