from django.forms import ModelForm

from courses.models import Voucher
from courses.utils import validate_amount_and_percentage, validate_amount, validate_percentage


class VoucherAdminForm(ModelForm):
    class Meta:
        model = Voucher
        fields = '__all__'

    def clean(self) -> dict:
        cleaned_data = super().clean()
        return validate_amount_and_percentage(cleaned_data)

    def clean_amount(self) -> int:
        return validate_amount(self.cleaned_data)

    def clean_percentage(self) -> int:
        return validate_percentage(self.cleaned_data)
