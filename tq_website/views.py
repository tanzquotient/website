import base64
import binascii
import datetime
import hmac
import logging
import uuid
from functools import wraps
from urllib.parse import urlencode

import requests
from allauth.account.adapter import get_adapter
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
    HttpResponseNotFound,
    HttpResponseRedirect,
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
)
from courses.views import PROFILE_REVIEW_SESSION_KEY

log = logging.getLogger("tq")


def require_metrics_auth(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        password = settings.METRICS.get("basic_auth_password", "")
        if not password:
            return HttpResponseNotFound()

        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        try:
            _user, _sep, pwd = (
                base64.b64decode(auth_header.removeprefix("Basic "))
                .decode()
                .partition(":")
            )
        except binascii.Error, UnicodeDecodeError:
            pwd = ""

        if hmac.compare_digest(pwd, password):
            return view(request, *args, **kwargs)

        response = HttpResponse(status=401)
        response["WWW-Authenticate"] = 'Basic realm="metrics"'
        return response

    return wrapped


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
_OIDC_IDP_ENDPOINTS = ["authorization_endpoint", "token_endpoint", "userinfo_endpoint"]


def _get_idp_config() -> dict | None:
    config = cache.get(_OIDC_IDP_CONFIG_CACHE_KEY)
    if config is None:
        try:
            response = requests.get(settings.OIDC_IDP_CONFIGURATION, timeout=5)
            response.raise_for_status()
            config = response.json()
        except (requests.exceptions.RequestException, ValueError) as e:
            log.warning("OIDC: could not load IdP configuration: %s", e)
            return None
        if not all(endpoint in config for endpoint in _OIDC_IDP_ENDPOINTS):
            log.warning("OIDC: IdP configuration is missing endpoints")
            return None
        cache.set(_OIDC_IDP_CONFIG_CACHE_KEY, config, timeout=3600)
    return config


_REQUIRED_USERINFO_CLAIMS = [
    "swissEduID",
    "swissEduPersonUniqueID",
    "given_name",
    "family_name",
    "email",
]

# Switch edu-ID omits multi-valued claims that have no values, e.g. users
# without a linked organisation get no swissEduIDLinkedAffiliation at all.
_OPTIONAL_USERINFO_LIST_CLAIMS = [
    "swissEduIDLinkedAffiliation",
    "swissEduIDLinkedAffiliationMail",
    "swissEduIDAssociatedMail",
]

_OIDC_ERROR_INVALID_REQUEST = _("This Switch edu-ID request is invalid.")
_OIDC_ERROR_SESSION = _(
    "Your Switch edu-ID sign-in has expired or was already completed. Please try again."
)
_OIDC_ERROR_IDP = _(
    "Something went wrong while communicating with Switch edu-ID. "
    "Please try again later."
)
_OIDC_ERROR_MISSING_CLAIMS = _(
    "Switch edu-ID did not provide all the information we need. Please try again later."
)
_OIDC_ERROR_WRONG_USER = _(
    "You are signed in to a different account than the one that started this "
    "request. Please try again."
)
_OIDC_ERROR_NOT_LINKED = _(
    "This Switch edu-ID is not the one linked to your account. Please sign in to "
    "Switch edu-ID with the account you linked."
)
# Same msgid as allauth's account_inactive template, so its translations apply.
_OIDC_ERROR_INACTIVE = _("This account is inactive.")


def _oidc_return_url(mode: str | None) -> str:
    return reverse("profile" if mode in ("link", "renew") else "account_login")


def _oidc_error(
    request: HttpRequest,
    mode: str | None,
    status: int,
    message: str,
    log_message: str,
    *log_args,
) -> HttpResponse:
    log.log(
        logging.ERROR if status >= 500 else logging.WARNING,
        "OIDC: " + log_message,
        *log_args,
    )
    return render(
        request,
        "oidc_result.html",
        {
            "mode": "error",
            "error_message": message,
            "redirect_url": _oidc_return_url(mode),
        },
        status=status,
    )


def oidc_login_view(request: HttpRequest) -> HttpResponse:
    mode = request.GET.get("mode")
    next_url = request.GET.get("next")

    if next_url and not url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}
    ):
        return _oidc_error(
            request,
            mode,
            403,
            _OIDC_ERROR_INVALID_REQUEST,
            "login rejected, next URL not allowed: %s",
            next_url,
        )

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
        return _oidc_error(
            request,
            mode,
            400,
            _OIDC_ERROR_INVALID_REQUEST,
            "login rejected, unknown mode: %s",
            mode,
        )

    idp_config = _get_idp_config()
    if idp_config is None:
        return _oidc_error(
            request, mode, 500, _OIDC_ERROR_IDP, "IdP configuration unavailable"
        )

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
        mode = request.session.pop("oidc_mode", None)
        for key in ("oidc_state", "oidc_redirect", "oidc_user_id"):
            request.session.pop(key, None)
        log.info("OIDC: authorization ended with error: %s", request.GET.get("error"))
        messages.error(
            request,
            _("Switch edu-ID authentication was cancelled or failed."),
            extra_tags="alert-danger",
        )
        return HttpResponseRedirect(_oidc_return_url(mode))

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
        return _oidc_error(
            request,
            mode,
            400,
            _OIDC_ERROR_SESSION,
            "callback rejected: code=%s mode=%s session_state=%s state_match=%s",
            bool(code),
            mode,
            state is not None,
            state == request.GET.get("state"),
        )

    idp_config = _get_idp_config()
    if idp_config is None:
        return _oidc_error(
            request, mode, 500, _OIDC_ERROR_IDP, "IdP configuration unavailable"
        )

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
    except requests.exceptions.RequestException as e:
        return _oidc_error(
            request, mode, 500, _OIDC_ERROR_IDP, "token request failed: %s", e
        )

    if token_response.status_code != 200:
        return _oidc_error(
            request,
            mode,
            500,
            _OIDC_ERROR_IDP,
            "token request returned %s: %s",
            token_response.status_code,
            token_response.text[:500],
        )

    try:
        token_data = token_response.json()
    except ValueError:
        return _oidc_error(
            request, mode, 500, _OIDC_ERROR_IDP, "token response is not JSON"
        )

    access_token = token_data.get("access_token")
    if not access_token:
        return _oidc_error(
            request,
            mode,
            500,
            _OIDC_ERROR_IDP,
            "token response has no access_token, keys: %s",
            sorted(token_data),
        )

    try:
        userinfo_response = requests.get(
            idp_config["userinfo_endpoint"],
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
    except requests.exceptions.RequestException as e:
        return _oidc_error(
            request, mode, 500, _OIDC_ERROR_IDP, "userinfo request failed: %s", e
        )

    if userinfo_response.status_code != 200:
        return _oidc_error(
            request,
            mode,
            500,
            _OIDC_ERROR_IDP,
            "userinfo request returned %s: %s",
            userinfo_response.status_code,
            userinfo_response.text[:500],
        )

    try:
        userinfo = userinfo_response.json()
    except ValueError:
        return _oidc_error(
            request, mode, 500, _OIDC_ERROR_IDP, "userinfo response is not JSON"
        )

    missing_claims = [k for k in _REQUIRED_USERINFO_CLAIMS if not userinfo.get(k)]
    if missing_claims:
        return _oidc_error(
            request,
            mode,
            500,
            _OIDC_ERROR_MISSING_CLAIMS,
            "userinfo is missing required claims: %s",
            missing_claims,
        )

    for claim in _OPTIONAL_USERINFO_LIST_CLAIMS:
        value = userinfo.get(claim) or []
        userinfo[claim] = [value] if isinstance(value, str) else value

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
    new_account = False

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
                        username=get_adapter(request).generate_unique_username(
                            [
                                userinfo["given_name"],
                                userinfo["family_name"],
                                userinfo["email"],
                                "user",
                            ]
                        ),
                        first_name=userinfo["given_name"],
                        last_name=userinfo["family_name"],
                        email=userinfo["email"],
                    )
                    user.emailaddress_set.create(
                        email=userinfo["email"], verified=True, primary=True
                    )
                # The post_save signal on User has already created the profile.
                switch_data.user_profile = user.profile
                new_account = True

    elif mode == "renew":
        if request.user.id != user_id:
            return _oidc_error(
                request,
                mode,
                403,
                _OIDC_ERROR_WRONG_USER,
                "renew rejected: signed in as user %s, flow started by user %s",
                request.user.id,
                user_id,
            )
        existing = _find_switch_data()
        if not existing or existing.user_profile_id != request.user.pk:
            return _oidc_error(
                request,
                mode,
                400,
                _OIDC_ERROR_NOT_LINKED,
                "renew rejected: edu-ID is not the one linked to user %s",
                request.user.id,
            )
        switch_data = existing
        user = request.user

    elif mode == "link":
        if request.user.id != user_id:
            return _oidc_error(
                request,
                mode,
                403,
                _OIDC_ERROR_WRONG_USER,
                "link rejected: signed in as user %s, flow started by user %s",
                request.user.id,
                user_id,
            )

        existing = _find_switch_data()
        if existing:
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
        return _oidc_error(
            request,
            mode,
            400,
            _OIDC_ERROR_INVALID_REQUEST,
            "callback rejected, unknown mode: %s",
            mode,
        )

    if mode == "login" and not user.is_active:
        return _oidc_error(
            request,
            mode,
            403,
            _OIDC_ERROR_INACTIVE,
            "login rejected: user %s is inactive",
            user.pk,
        )

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
        if already_linked_elsewhere:
            logout(request)
        # allauth redirects to `redirect_url`, or returns its own response if
        # the login could not be completed.
        response = perform_login(
            request,
            user,
            email_verification="none",
            redirect_url=reverse("edit_profile") if new_account else redirect,
        )
        if new_account and request.user.is_authenticated:
            request.session[PROFILE_REVIEW_SESSION_KEY] = True
        if already_linked_elsewhere and request.user.is_authenticated:
            return render(
                request,
                "oidc_result.html",
                {
                    "mode": "already_linked",
                    "redirect_url": redirect,
                },
            )
        return response

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
