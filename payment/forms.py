from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from courses.models import Subscribe

def validate_usi_exists(value):
    if not Subscribe.objects.filter(usi=value).count() > 0:
        raise ValidationError('The specified USI does not exist')

class USIForm(forms.Form):
    usi_validator = RegexValidator(regex='[a-zA-Z0-9]{6}', message="Please enter a valid USI")
    usi = forms.CharField(max_length=6, label="Unique Course Identifier (USI)", validators=[usi_validator, validate_usi_exists, ])

