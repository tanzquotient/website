from django.core.exceptions import ValidationError
from django.forms import ModelForm

from courses.models import Voucher


class VoucherAdminForm(ModelForm):
    class Meta:
        model = Voucher
        fields = '__all__'

    def clean(self) -> dict:
        cleaned_data = super().clean()

        amount = cleaned_data.get('amount')
        percentage = cleaned_data.get('percentage')

        if not amount and not percentage:
            raise ValidationError('You need to set either the amount or percentage.')
        if amount and percentage:
            raise ValidationError('You are not allowed to set both amount and percentage.')

        return cleaned_data

    def clean_amount(self) -> dict:
        amount = self.cleaned_data.get('amount')
        if amount and amount < 0:
            raise ValidationError('The amount must be non-negative')
        return amount

    def clean_percentage(self) -> dict:
        percentage = self.cleaned_data.get('percentage')
        if percentage and (percentage < 0 or percentage > 100):
            raise ValidationError('The percentage must be between 0 and 100')
        return percentage
