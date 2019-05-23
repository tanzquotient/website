from datetime import date

from django import forms
from django.utils.translation import ugettext_lazy
from django_countries.fields import LazyTypedChoiceField

from courses.models import UserProfile
from django_countries import countries


class UserEditForm(forms.Form):

    phone_number = forms.CharField(max_length=255, required=False)
    phone_number.label = ugettext_lazy('Telephone number (Mobile)')
    phone_number.help_text = 'Deine Nummer wird nur für interne Zwecke verwendet und den Lehrern für das Teilen von Kursinhalten weitergegeben!'
    student_status = forms.ChoiceField(choices=UserProfile.StudentStatus.CHOICES)
    student_status.label = ugettext_lazy('Student')
    gender = forms.ChoiceField(choices=UserProfile.Gender.CHOICES)
    gender.label = ugettext_lazy('Gender')
    body_height = forms.IntegerField(max_value=400, required=False)
    body_height.label = ugettext_lazy('Height (cm)')
    body_height.help_text = 'Die Körpergrösse (in cm) kann bei Einzelanmeldungen angegeben werden zum finden eines ähnlich grossen Partners.'
    legi = forms.CharField(max_length=16, required=False)
    legi.label = ugettext_lazy('Student card number')
    newsletter = forms.BooleanField(required=False, initial=True)
    newsletter.label = ugettext_lazy('Subscribe to newsletter')
    get_involved = forms.BooleanField(required=False)
    get_involved.label = ugettext_lazy('I\'d like to help TQ from time to time (Events etc.)')
    street = forms.CharField(max_length=255)
    street.label = ugettext_lazy('Street')
    plz = forms.IntegerField()
    plz.label = ugettext_lazy('Postal code')
    city = forms.CharField(max_length=255)
    city.label = ugettext_lazy('City')
    birthdate = forms.DateField(required=False, widget=forms.widgets.SelectDateWidget(
        empty_label=("Choose Year", "Choose Month", "Choose Day"),
        years=range(date.today().year - 70, date.today().year - 10)))

    picture = forms.ImageField(required=False)
    about_me = forms.CharField(widget=forms.Textarea(), required=False)
    about_me.help_text = 'Tipp: Hier kann auch HTML Code zum Formatieren eingegeben werden!'
    nationality = LazyTypedChoiceField(choices=countries, required=False)
    residence_permit = forms.ChoiceField(choices=UserProfile.Residence.CHOICES, required=False)
    ahv_number = forms.CharField(max_length=255, required=False)
    iban = forms.CharField(max_length=255, required=False)
    bank_name = forms.CharField(max_length=255, required=False)
    bank_zip_code = forms.CharField(max_length=255, required=False)
    bank_city = forms.CharField(max_length=255, required=False)
    bank_country = LazyTypedChoiceField(choices=countries, required=False)


def clean(self):
        cleaned_data = super(UserEditForm, self).clean()

        # if a student, the legi must be set
        if cleaned_data.get('student_status') != 'no' and not cleaned_data.get('legi'):
            msg = ugettext_lazy("Students have to enter their student card number.")
            self.add_error('legi', msg)
            raise forms.ValidationError(msg)

        return cleaned_data
