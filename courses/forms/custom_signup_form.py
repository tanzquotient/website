import logging

from django import forms

from courses.forms import UserEditForm
from courses.models import Gender
from courses.services import update_user

log = logging.getLogger('tq')


class CustomSignupForm(UserEditForm):
    first_name = forms.CharField(max_length=30)
    first_name.label = 'Vorname'
    last_name = forms.CharField(max_length=30)
    last_name.label = 'Nachname'
    gender = forms.ChoiceField(choices=Gender.CHOICES)
    gender.label = 'Geschlecht'

    def signup(self, request, user):
        log.info("signup new user with email {}".format(user.email))
        update_user(user, self.cleaned_data)