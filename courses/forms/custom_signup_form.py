import logging

from django.contrib.auth.models import User
from django.http import HttpRequest

from courses.forms.user_edit_from import UserEditForm
from courses.services.users import update_user

log = logging.getLogger("tq")


class CustomSignupForm(UserEditForm):
    def signup(self, request: HttpRequest, user: User) -> None:
        log.info(f"signup new user with email {user.email}")
        update_user(user, self.cleaned_data)
