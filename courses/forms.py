from django import forms

from .models import UserProfile
from .services import update_user

import logging

log = logging.getLogger('tq')


class UserEditForm(forms.Form):
    phone_number = forms.CharField(max_length=255, required=False)
    phone_number.label = 'Telefonnummer (Mobile)'
    student_status = forms.ChoiceField(choices=UserProfile.StudentStatus.CHOICES)
    student_status.label = 'Student'
    legi = forms.CharField(max_length=16, required=False)
    legi.label = 'Legi-Nummer'
    newsletter = forms.BooleanField(required=False, initial=True)
    newsletter.label = 'Newsletter abonnieren'
    get_involved = forms.BooleanField(required=False)
    get_involved.label = 'Ich würde gerne ab und zu beim TQ mithelfen (Events etc.)'

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

    class Meta:
        fields=['first_name', 'last_name','gender','phone_number','student_status','legi','newsletter','get_involved']

    def signup(self, request, user):
        log.info("signup new user with email {}".format(user.email))
        update_user(user, self.cleaned_data)


class UserForm(CustomSignupForm):
    street = forms.CharField(max_length=255)
    street.label = 'Strasse'
    plz = forms.IntegerField()
    plz.label = 'PLZ'
    city = forms.CharField(max_length=255)
    city.label = 'Ort'
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
    return initial
