from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from courses.models import Subscribe, Voucher
import datetime
from django.utils.translation import ugettext as _

def validate_usi_exists(value):
    if not Subscribe.objects.filter(usi=value).count() > 0:
        raise ValidationError(_('The specified USI does not exist'))

def voucher_valid(value):
    if not Voucher.objects.filter(key=value).count() > 0:
        raise ValidationError(_('The specified voucher code does not exist'))
    voucher = Voucher.objects.filter(key=value).first()
    if not voucher.used == False:
        raise ValidationError(_('The specified voucher code has already been used'))
    if voucher.expires:
        if not voucher.expires >= datetime.datetime.today().date():
            raise ValidationError(_('The specified voucher code is expired'))


class USIForm(forms.Form):
    usi_validator = RegexValidator(regex='[a-zA-Z0-9]{6}', message=_("Please enter a valid USI"))
    usi = forms.CharField(max_length=6, label=_("Unique Course Identifier (USI)"), validators=[usi_validator, validate_usi_exists, ])

class VoucherForm(forms.Form):
    voucher_code = forms.CharField(max_length=6, label=_("Voucher Code"), validators=[voucher_valid,  ])

