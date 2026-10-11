import base64
import datetime
import hashlib
import json
import logging
import secrets
import time
import uuid
from urllib.parse import urlencode

import requests
from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
from allauth.account.utils import perform_login
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import transaction
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from courses.models import (
    SwitchData,
    SwitchDataAffiliation,
    SwitchDataAffiliationEmail,
    SwitchDataAssociatedEmail,
)
from courses.views import PROFILE_REVIEW_SESSION_KEY

log = logging.getLogger("tq")

_OIDC_IDP_CONFIG_CACHE_KEY = "oidc_idp_config"
_OIDC_IDP_CONFIG_KEYS = [
    "issuer",
    "authorization_endpoint",
    "token_endpoint",
    "userinfo_endpoint",
]
_OIDC_SESSION_KEYS = [
    "oidc_state",
    "oidc_nonce",
    "oidc_code_verifier",
    "oidc_redirect",
    "oidc_mode",
    "oidc_user_id",
]
_OIDC_SWITCH_SESSION_KEY = "oidc_pending_account_switch"
_OIDC_SWITCH_TIMEOUT_SECONDS = 300
_OIDC_CLOCK_SKEW_SECONDS = 60


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
        if not all(key in config for key in _OIDC_IDP_CONFIG_KEYS):
            log.warning("OIDC: IdP configuration is missing required keys")
            return None
        cache.set(_OIDC_IDP_CONFIG_CACHE_KEY, config, timeout=3600)
    return config


def _pkce_challenge(code_verifier: str) -> str:
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


class _IdTokenError(Exception):
    pass


def _id_token_claims(id_token, issuer: str, nonce: str) -> dict:
    """Check the ID token returned by the token endpoint and return its claims.

    The signature is not verified: the token comes straight from the token
    endpoint over TLS, which OIDC Core 3.1.3.7 accepts in place of it.
    """
    if not isinstance(id_token, str):
        raise _IdTokenError("missing")
    try:
        payload = id_token.split(".")[1]
        claims = json.loads(
            base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4))
        )
    except (IndexError, ValueError) as e:
        raise _IdTokenError(f"malformed: {e}") from e
    if not isinstance(claims, dict):
        raise _IdTokenError("malformed: payload is not an object")

    if claims.get("iss") != issuer:
        raise _IdTokenError(f"issuer {claims.get('iss')!r} is not {issuer!r}")
    audience = claims.get("aud")
    audiences = [audience] if isinstance(audience, str) else audience or []
    if settings.OIDC_CLIENT_ID not in audiences:
        raise _IdTokenError(f"audience {audience!r} does not contain our client")
    if len(audiences) > 1 and claims.get("azp") != settings.OIDC_CLIENT_ID:
        raise _IdTokenError(f"authorized party {claims.get('azp')!r} is not our client")
    expires = claims.get("exp")
    if not isinstance(expires, int | float):
        raise _IdTokenError("no expiry")
    if expires + _OIDC_CLOCK_SKEW_SECONDS < time.time():
        raise _IdTokenError("expired")
    if claims.get("nonce") != nonce:
        raise _IdTokenError("nonce does not match")
    if not claims.get("sub"):
        raise _IdTokenError("no subject")
    return claims


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
_OIDC_ERROR_EMAIL_IN_USE = _(
    "An account with your email address already exists. Please sign in with your "
    "password (or reset it) and connect Switch edu-ID from your profile."
)


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
        next_url,
        allowed_hosts={request.get_host()},
        # request.is_secure() is always False behind our proxy (there is no
        # SECURE_PROXY_SSL_HEADER), but production only serves HTTPS.
        require_https=not settings.DEBUG,
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
    nonce = secrets.token_urlsafe(32)
    code_verifier = secrets.token_urlsafe(64)
    request.session["oidc_state"] = state
    request.session["oidc_nonce"] = nonce
    request.session["oidc_code_verifier"] = code_verifier
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
        "nonce": nonce,
        "code_challenge": _pkce_challenge(code_verifier),
        "code_challenge_method": "S256",
    }

    authorization_url = f"{idp_config['authorization_endpoint']}?{urlencode(params)}"
    return HttpResponseRedirect(authorization_url)


def oidc_callback_view(request: HttpRequest) -> HttpResponse:
    if request.GET.get("error"):
        mode = request.session.get("oidc_mode")
        for key in _OIDC_SESSION_KEYS:
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
    nonce = request.session.pop("oidc_nonce", None)
    code_verifier = request.session.pop("oidc_code_verifier", None)
    redirect = request.session.pop("oidc_redirect", None) or reverse("user_courses")
    mode = request.session.pop("oidc_mode", None)
    user_id = request.session.pop("oidc_user_id", None)

    if (
        not code
        or not mode
        or not nonce
        or not code_verifier
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
                "code_verifier": code_verifier,
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
        id_token_claims = _id_token_claims(
            token_data.get("id_token"), idp_config["issuer"], nonce
        )
    except _IdTokenError as e:
        return _oidc_error(
            request, mode, 500, _OIDC_ERROR_IDP, "ID token rejected: %s", e
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

    # OIDC Core 5.3.2: the UserInfo sub must match the ID token sub.
    if userinfo.get("sub") != id_token_claims["sub"]:
        return _oidc_error(
            request,
            mode,
            500,
            _OIDC_ERROR_IDP,
            "userinfo sub does not match the ID token sub",
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
            verified_owners = set(
                EmailAddress.objects.filter(email_query, verified=True).values_list(
                    "user", flat=True
                )
            )
            if len(verified_owners) == 1:
                user = User.objects.get(pk=verified_owners.pop())
                switch_data.user_profile = user.profile
            elif (
                verified_owners
                or EmailAddress.objects.filter(email_query).exists()
                or User.objects.filter(email_query).exists()
            ):
                # Several accounts, or only unverified ones: we cannot tell which
                # account is theirs, so they have to sign in and link it.
                return _oidc_error(
                    request,
                    mode,
                    409,
                    _OIDC_ERROR_EMAIL_IN_USE,
                    "login rejected: edu-ID email addresses already in use "
                    "(%s verified owners)",
                    len(verified_owners),
                )
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
            # The edu-ID belongs to another account: ask before switching to it.
            other = existing.user_profile.user
            if not other.is_active:
                return _oidc_error(
                    request,
                    mode,
                    403,
                    _OIDC_ERROR_INACTIVE,
                    "link rejected: edu-ID belongs to inactive user %s",
                    other.pk,
                )
            request.session[_OIDC_SWITCH_SESSION_KEY] = {
                "user_id": other.pk,
                "expires": time.time() + _OIDC_SWITCH_TIMEOUT_SECONDS,
                "redirect": redirect,
            }
            return render(
                request,
                "oidc_result.html",
                {
                    "mode": "confirm_switch",
                    "other_account": other.email or other.username,
                    "redirect_url": reverse("profile"),
                },
            )
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


@require_POST
def oidc_switch_account_view(request: HttpRequest) -> HttpResponse:
    """Sign in to the account an edu-ID is linked to, after the user confirmed it."""
    pending = request.session.pop(_OIDC_SWITCH_SESSION_KEY, None)
    if not pending or pending["expires"] < time.time():
        return _oidc_error(
            request,
            "link",
            400,
            _OIDC_ERROR_SESSION,
            "account switch rejected: no pending switch or it expired",
        )

    user = User.objects.filter(pk=pending["user_id"]).first()
    if user is None or not user.is_active:
        return _oidc_error(
            request,
            "link",
            403,
            _OIDC_ERROR_INACTIVE,
            "account switch rejected: user %s is missing or inactive",
            pending["user_id"],
        )

    logout(request)
    response = perform_login(request, user, email_verification="none")
    if not request.user.is_authenticated:
        return response
    return render(
        request,
        "oidc_result.html",
        {"mode": "already_linked", "redirect_url": pending["redirect"]},
    )
