from django import forms

from . import VoucherForm


class CreateSendVoucherForm(VoucherForm):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
