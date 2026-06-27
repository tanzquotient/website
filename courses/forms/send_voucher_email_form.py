from django import forms

from .voucher_email_form import VoucherEmailForm


class SendVoucherEmailForm(VoucherEmailForm):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
