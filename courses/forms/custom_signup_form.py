import logging

from django.contrib.auth.models import User
from django.http import HttpRequest

from courses.forms import UserEditForm
from courses.services import update_user

log = logging.getLogger("tq")


class CustomSignupForm(UserEditForm):
    def signup(self, request: HttpRequest, user: User) -> None:
        log.info("signup new user with email {}".format(user.email))
        update_user(user, self.cleaned_data)
