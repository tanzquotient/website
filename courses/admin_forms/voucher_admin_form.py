from django.forms import ModelForm

from courses.models import Voucher
from courses.utils import validate_amount


class VoucherAdminForm(ModelForm):
    class Meta:
        model = Voucher
        fields = "__all__"

    def clean_amount(self) -> int:
        return validate_amount(self.cleaned_data)
