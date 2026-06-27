import datetime
import uuid
from urllib.parse import urlencode

import requests
from allauth.account.models import EmailAddress
from allauth.account.utils import perform_login
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.cache import cache
from django.db import transaction
from django.db.models import Q
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseRedirect,
    HttpResponseServerError,
)
from django.shortcuts import render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _
from django.views.generic import RedirectView

from courses.models import (
    SwitchData,
    SwitchDataAffiliation,
    SwitchDataAffiliationEmail,
    SwitchDataAssociatedEmail,
    UserProfile,
)
from courses.services import find_unused_username_variant


class WellKnownRedirectView(RedirectView):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        path = kwargs.get("path")
        # Note the missing dot in the directory name.
        # This is to make S3 happy, which ignores dot-files/dot-dirs during collectstatic.
        url = (
            staticfiles_storage.url(f"well-known/{path}")
            if settings.S3_ENABLED
            else f"{settings.STATIC_URL}well-known/{path}"
        )
        return url


_OIDC_IDP_CONFIG_CACHE_KEY = "oidc_idp_config"


def _get_idp_config() -> dict | None:
    config = cache.get(_OIDC_IDP_CONFIG_CACHE_KEY)
    if config is None:
        try:
            config = requests.get(settings.OIDC_IDP_CONFIGURATION, timeout=5).json()
        except requests.exceptions.RequestException, ValueError:
            return None
        cache.set(_OIDC_IDP_CONFIG_CACHE_KEY, config, timeout=3600)
    return config


_REQUIRED_USERINFO_CLAIMS = [
    "swissEduID",
    "swissEduPersonUniqueID",
    "given_name",
    "family_name",
    "email",
    "swissEduIDLinkedAffiliation",
    "swissEduIDLinkedAffiliationMail",
    "swissEduIDAssociatedMail",
]


def oidc_login_view(request: HttpRequest) -> HttpResponse:
    mode = request.GET.get("mode")
    next_url = request.GET.get("next")

    if next_url and not url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}
    ):
        return HttpResponseForbidden()

    if mode == "link":
        if request.user.is_anonymous:
            return HttpResponseRedirect(
                reverse("account_login") + "?next=" + reverse("profile")
            )
        if request.user.profile.has_switch():
            messages.add_message(
                request,
                messages.WARNING,
                _("Switch edu-ID is already linked to your account."),
                extra_tags="alert-warning",
            )
            return HttpResponseRedirect(reverse("profile"))
    elif mode == "login":
        if not request.user.is_anonymous:
            return HttpResponseRedirect(next_url or reverse("user_courses"))
    elif mode == "renew":
        if request.user.is_anonymous:
            return HttpResponseRedirect(
                reverse("account_login") + "?next=" + reverse("profile")
            )
        if not request.user.profile.has_switch():
            return HttpResponseRedirect(reverse("profile"))
    else:
        return HttpResponseBadRequest()

    idp_config = _get_idp_config()
    if idp_config is None:
        return HttpResponseServerError()

    state = str(uuid.uuid4())
    request.session["oidc_state"] = state
    request.session["oidc_redirect"] = next_url
    request.session["oidc_mode"] = mode
    if mode in ("link", "renew"):
        request.session["oidc_user_id"] = request.user.id

    params = {
        "response_type": "code",
        "client_id": settings.OIDC_CLIENT_ID,
        "redirect_uri": settings.OIDC_REDIRECT_URI,
        "scope": settings.OIDC_SCOPES,
        "state": state,
    }

    authorization_url = f"{idp_config['authorization_endpoint']}?{urlencode(params)}"
    return HttpResponseRedirect(authorization_url)


def oidc_callback_view(request: HttpRequest) -> HttpResponse:
    if request.GET.get("error"):
        messages.error(
            request,
            _("Switch edu-ID authentication was cancelled or failed."),
            extra_tags="alert-danger",
        )
        return HttpResponseRedirect(reverse("account_login"))

    code = request.GET.get("code")

    state = request.session.pop("oidc_state", None)
    redirect = request.session.pop("oidc_redirect", None) or reverse("user_courses")
    mode = request.session.pop("oidc_mode", None)
    user_id = request.session.pop("oidc_user_id", None)

    if (
        not code
        or not mode
        or state != request.GET.get("state")
        or (mode in ("link", "renew") and not user_id)
    ):
        return HttpResponseBadRequest()

    idp_config = _get_idp_config()
    if idp_config is None:
        return HttpResponseServerError()

    try:
        token_response = requests.post(
            idp_config["token_endpoint"],
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.OIDC_REDIRECT_URI,
                "client_id": settings.OIDC_CLIENT_ID,
                "client_secret": settings.OIDC_CLIENT_SECRET,
            },
            timeout=10,
        )
    except requests.exceptions.RequestException:
        return HttpResponseServerError()

    if token_response.status_code != 200:
        return HttpResponseServerError()

    try:
        token_data = token_response.json()
    except ValueError:
        return HttpResponseServerError()

    access_token = token_data.get("access_token")
    if not access_token:
        return HttpResponseServerError()

    try:
        userinfo_response = requests.get(
            idp_config["userinfo_endpoint"],
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
    except requests.exceptions.RequestException:
        return HttpResponseServerError()

    if userinfo_response.status_code != 200:
        return HttpResponseServerError()

    try:
        userinfo = userinfo_response.json()
    except ValueError:
        return HttpResponseServerError()

    if any(k not in userinfo for k in _REQUIRED_USERINFO_CLAIMS):
        return HttpResponseServerError()

    def _find_switch_data():
        try:
            return SwitchData.objects.select_related("user_profile__user").get(
                swiss_edu_id=userinfo["swissEduID"]
            )
        except SwitchData.DoesNotExist:
            pass
        try:
            return SwitchData.objects.select_related("user_profile__user").get(
                swiss_edu_person_unique_id=userinfo["swissEduPersonUniqueID"]
            )
        except SwitchData.DoesNotExist:
            return None

    already_linked_elsewhere = False

    if mode == "login":
        if not request.user.is_anonymous:
            return HttpResponseRedirect(redirect)

        existing = _find_switch_data()
        if existing:
            switch_data = existing
            user = existing.user_profile.user
        else:
            switch_data = SwitchData(
                swiss_edu_person_unique_id=userinfo["swissEduPersonUniqueID"]
            )
            email_query = Q()
            for email in set(
                [userinfo["email"]]
                + userinfo["swissEduIDLinkedAffiliationMail"]
                + userinfo["swissEduIDAssociatedMail"]
            ):
                email_query |= Q(email__iexact=email)
            email_addresses = EmailAddress.objects.filter(verified=True).filter(
                email_query
            )
            users_with_email = User.objects.filter(
                pk__in=list(set(email_addresses.values_list("user", flat=True)))
            ).distinct()
            if users_with_email.count() == 1:
                user = users_with_email.get()
                switch_data.user_profile = user.profile
            else:
                with transaction.atomic():
                    user = User.objects.create(
                        username=find_unused_username_variant(userinfo["given_name"]),
                        first_name=userinfo["given_name"],
                        last_name=userinfo["family_name"],
                        email=userinfo["email"],
                    )
                    profile = UserProfile.objects.create(user=user)
                    user.emailaddress_set.create(email=userinfo["email"], verified=True)
                switch_data.user_profile = profile

    elif mode == "renew":
        if request.user.id != user_id:
            return HttpResponseForbidden()
        existing = _find_switch_data()
        if not existing or existing.user_profile_id != request.user.pk:
            return HttpResponseBadRequest()
        switch_data = existing
        user = request.user

    elif mode == "link":
        if request.user.id != user_id:
            return HttpResponseForbidden()

        existing = _find_switch_data()
        if existing:
            logout(request)
            mode = "login"
            already_linked_elsewhere = True
            switch_data = existing
            user = existing.user_profile.user
        else:
            switch_data = SwitchData(
                swiss_edu_person_unique_id=userinfo["swissEduPersonUniqueID"]
            )
            user = request.user
            switch_data.user_profile = user.profile

    else:
        return HttpResponseBadRequest()

    with transaction.atomic():
        switch_data.swiss_edu_id = userinfo["swissEduID"]
        switch_data.given_name = userinfo["given_name"]
        switch_data.family_name = userinfo["family_name"]
        switch_data.email = userinfo["email"]
        switch_data.save()
        switch_data.affiliation_emails.all().delete()
        switch_data.associated_emails.all().delete()
        switch_data.affiliations.all().delete()
        SwitchDataAffiliationEmail.objects.bulk_create(
            [
                SwitchDataAffiliationEmail(switch_data=switch_data, email=email)
                for email in set(userinfo["swissEduIDLinkedAffiliationMail"])
            ]
        )
        SwitchDataAssociatedEmail.objects.bulk_create(
            [
                SwitchDataAssociatedEmail(switch_data=switch_data, email=email)
                for email in set(userinfo["swissEduIDAssociatedMail"])
            ]
        )
        SwitchDataAffiliation.objects.bulk_create(
            [
                SwitchDataAffiliation(switch_data=switch_data, affiliation=affiliation)
                for affiliation in set(userinfo["swissEduIDLinkedAffiliation"])
            ]
        )
        is_student_now = switch_data.is_student()
        if is_student_now:
            user.profile.student_validity = datetime.date.today() + datetime.timedelta(
                days=180
            )
            user.profile.save()

    if mode == "renew":
        return render(
            request,
            "oidc_result.html",
            {
                "mode": "renew",
                "is_student": is_student_now,
                "student_validity": user.profile.student_validity,
                "redirect_url": reverse("profile"),
            },
        )

    if mode == "login":
        perform_login(request, user, email_verification="none")
        if already_linked_elsewhere:
            return render(
                request,
                "oidc_result.html",
                {
                    "mode": "already_linked",
                    "redirect_url": redirect,
                },
            )
        messages.success(
            request,
            _("Signed in via Switch edu-ID."),
            extra_tags="alert-success",
        )
        return HttpResponseRedirect(redirect)

    return render(
        request,
        "oidc_result.html",
        {
            "mode": "link",
            "is_student": is_student_now,
            "student_validity": user.profile.student_validity,
            "redirect_url": reverse("profile"),
        },
    )
