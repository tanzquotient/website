from django import forms

from . import EmailVoucherForm


class SendEmailVoucherForm(EmailVoucherForm):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
