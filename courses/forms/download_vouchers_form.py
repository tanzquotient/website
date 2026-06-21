from django import forms


class DownloadVouchersForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput())
    format = forms.ChoiceField(
        choices=[
            ("pdf", "Single PDF (all vouchers combined into one file)"),
            ("zip", "ZIP archive (one PDF per voucher)"),
        ],
        widget=forms.RadioSelect,
        initial="pdf",
        label="Download format",
    )
