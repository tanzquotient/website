from datetime import date

from django import forms
from django.core.exceptions import ValidationError
from django_countries import countries
from django_countries.fields import LazyTypedChoiceField

from courses.forms import UserEditForm
from courses.models import UserProfile


def validate(birth_date):
    if birth_date == date(year=1920, month=1, day=1):
        raise ValidationError("Please insert your birth date")


class TeacherEditForm(UserEditForm):

    birthdate = forms.DateField(required=True, validators=[validate], widget=forms.widgets.SelectDateWidget(
        years=range(1920, date.today().year - 10))
                                )
    nationality = LazyTypedChoiceField(choices=countries, required=True)
    residence_permit = forms.ChoiceField(choices=UserProfile.Residence.CHOICES, required=True)
    ahv_number = forms.CharField(max_length=255, required=True)
    iban = forms.CharField(max_length=255, required=False)
    bank_name = forms.CharField(max_length=255, required=True)
    bank_zip_code = forms.CharField(max_length=255, required=True)
    bank_city = forms.CharField(max_length=255, required=True)
    bank_country = LazyTypedChoiceField(choices=countries, required=True)


