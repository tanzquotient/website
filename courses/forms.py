from django import forms

from .models import UserProfile
from .services import update_user
from django_countries.fields import LazyTypedChoiceField
from django_countries import countries
import logging
from datetime import date
from django.utils.translation import ugettext

log = logging.getLogger('tq')


class UserEditForm(forms.Form):
    phone_number = forms.CharField(max_length=255, required=False)
    phone_number.label = ugettext('Telephone number (Mobile)')
    phone_number.help_text = 'Deine Nummer wird nur für interne Zwecke verwendet und den Lehrern für das Teilen von Kursinhalten weitergegeben!'
    student_status = forms.ChoiceField(choices=UserProfile.StudentStatus.CHOICES)
    student_status.label = 'Student'
    legi = forms.CharField(max_length=16, required=False)
    legi.label = 'Legi-Nummer'
    newsletter = forms.BooleanField(required=False, initial=True)
    newsletter.label = 'Newsletter abonnieren'
    get_involved = forms.BooleanField(required=False)
    get_involved.label = 'Ich würde gerne ab und zu beim TQ mithelfen (Events etc.)'
    street = forms.CharField(max_length=255)
    street.label = 'Strasse'
    plz = forms.IntegerField()
    plz.label = 'PLZ'
    city = forms.CharField(max_length=255)
    city.label = 'Ort'

    birthdate = forms.DateField(required=False, widget=forms.widgets.SelectDateWidget(
        empty_label=("Choose Year", "Choose Month", "Choose Day"),
        years=range(date.today().year - 70, date.today().year - 10)))
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
            msg = "Legi muss fuer Studenten angegeben werden."
            self.add_error('legi', msg)
            raise forms.ValidationError(msg)

        return cleaned_data


class CustomSignupForm(UserEditForm):
    first_name = forms.CharField(max_length=30)
    first_name.label = 'Vorname'
    last_name = forms.CharField(max_length=30)
    last_name.label = 'Nachname'
    gender = forms.ChoiceField(choices=UserProfile.Gender.CHOICES)
    gender.label = 'Geschlecht'

    def signup(self, request, user):
        log.info("signup new user with email {}".format(user.email))
        update_user(user, self.cleaned_data)


class UserForm(CustomSignupForm):
    email = forms.EmailField(max_length=75)
    email.label = 'E-Mail'
    email.help_text = 'Bitte gib die persönliche E-Mail Adresse für dich und deinen Partner separat an!'
    email_repetition = forms.EmailField(max_length=75)
    email_repetition.label = 'E-Mail Wiederholung'
    body_height = forms.IntegerField(max_value=400, required=False)
    body_height.label = 'Körpergrösse (cm)'
    body_height.help_text = 'Die Körpergrösse (in cm) kann bei Einzelanmeldungen angegeben werden zum finden eines ähnlich grossen Partners.'
    experience = forms.CharField(widget=forms.Textarea, max_length=1000, required=False)
    experience.label = 'Erfahrung'
    comment = forms.CharField(widget=forms.Textarea, max_length=1000, required=False)
    comment.label = 'Kommentar'
    general_terms = forms.BooleanField(required=True)
    general_terms.label = 'I accept that the enrollment is binding.'

    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        email = cleaned_data.get("email")
        email_repetition = cleaned_data.get("email_repetition")

        if email != email_repetition:
            msg = "Email-Adressen sind nicht gleich."
            self.add_error('email_repetition', msg)
            raise forms.ValidationError(msg)

        return cleaned_data


def create_initial_from_user(user, initial={}):
    initial['first_name'] = user.first_name
    initial['last_name'] = user.last_name
    initial['gender'] = user.profile.gender
    initial['phone_number'] = user.profile.phone_number
    initial['student_status'] = user.profile.student_status
    initial['legi'] = user.profile.legi
    initial['newsletter'] = user.profile.newsletter
    initial['get_involved'] = user.profile.get_involved
    if user.profile.address:
        initial['street'] = user.profile.address.street
        initial['plz'] = user.profile.address.plz
        initial['city'] = user.profile.address.city
    initial['email'] = user.email
    initial['email_repetition'] = user.email
    initial['body_height'] = user.profile.body_height

    initial['birthdate'] = user.profile.birthdate
    initial['nationality'] = user.profile.nationality
    initial['residence_permit'] = user.profile.residence_permit
    initial['ahv_number'] = user.profile.ahv_number
    if user.profile.bank_account:
        initial['iban'] = user.profile.bank_account.iban
        initial['bank_name'] = user.profile.bank_account.bank_name
        initial['bank_zip_code'] = user.profile.bank_account.bank_zip_code
        initial['bank_city'] = user.profile.bank_account.bank_city
        initial['bank_country'] = user.profile.bank_account.bank_country

    return initial
