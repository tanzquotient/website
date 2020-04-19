import datetime

from django import forms
from django.forms.widgets import SelectDateWidget
from django.utils.translation import ugettext as _

from courses.models import *


class VoucherGenerationForm(forms.Form):
    number_of_vouchers = forms.IntegerField(label=_("How many voucher should be generated?"), initial=20)
    percentage = forms.IntegerField(label=_("Percentage of voucher"), initial=100)
    purpose = forms.ModelChoiceField(queryset=VoucherPurpose.objects)
    expires_flag = forms.BooleanField(label=_("Set expire date?"), initial=False, required=False)
    expires = forms.DateField(widget=SelectDateWidget, initial=datetime.date.today() + datetime.timedelta(days=365 * 2))