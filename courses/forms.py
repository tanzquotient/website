from django import forms

from .models import UserProfile
from .services import update_user
from django_countries.fields import LazyTypedChoiceField
from django_countries import countries
import logging
from datetime import date
from django.utils.translation import ugettext, ugettext_lazy

log = logging.getLogger('tq')


class UserEditForm(forms.Form):
    phone_number = forms.CharField(max_length=255, required=False)
    phone_number.label = ugettext_lazy('Telephone number (Mobile)')
    phone_number.help_text = 'Deine Nummer wird nur für interne Zwecke verwendet und den Lehrern für das Teilen von Kursinhalten weitergegeben!'
    student_status = forms.ChoiceField(choices=UserProfile.StudentStatus.CHOICES)
    student_status.label = ugettext_lazy('Student')
    legi = forms.CharField(max_length=16, required=False)
    legi.label = ugettext('Student card number')
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
            msg = ugettex("Students have to enter their student card number.")
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

class SingleSubscriptionForm(forms.Form):
    textarea_attribs = {'rows': '4', 'cols': '80'}
    experience = forms.CharField(widget=forms.Textarea(textarea_attribs), max_length=1000, required=False)
    experience.label = 'Erfahrung'
    comment = forms.CharField(widget=forms.Textarea(textarea_attribs), max_length=1000, required=False)
    comment.label = 'Kommentar'
    
    general_terms = forms.BooleanField(required=True)
    general_terms.label = 'I/We accept that the enrollment is binding.'
        

class CoupleSubscriptionForm(SingleSubscriptionForm):
    # helper function that checks if the email address belongs to a user
    def validate_user_email(email):
        # an empty address is ok
        if not email:
            return
        users = UserProfile.objects.filter(user__email=email)
        # the email does not belong to a valid user account
        if len(users) != 1:
            raise forms.ValidationError('There is no user for the email address you entered for your partner!')
    
    partner_email = forms.EmailField(required=False, validators=[validate_user_email])        
