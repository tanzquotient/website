from django import forms

from . import VoucherForm


class SendVoucherForm(VoucherForm):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
