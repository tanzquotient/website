import uuid
import json
import requests
import datetime
from urllib.parse import urlencode

from django.conf import settings
from django.contrib import messages
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic import RedirectView
from django.contrib.auth import logout
from django.db.models import Q
from allauth.account.utils import perform_login
from allauth.account.models import EmailAddress
from django.contrib.auth.models import User
from django.conf import settings
from django.urls import reverse
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
    HttpResponseForbidden,
    HttpResponseServerError,
)
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _

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


def oidc_login_view(request: HttpRequest) -> HttpResponse:

    if request.GET.get("next") and not url_has_allowed_host_and_scheme(
        request.GET.get("next")
    ):
        return HttpResponseForbidden()

    state = str(uuid.uuid4())

    request.session["oidc_state"] = state
    request.session["oidc_redirect"] = request.GET.get("next")
    request.session["oidc_mode"] = request.GET.get("mode")

    if request.session["oidc_mode"] == "link":
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
        request.session["oidc_user_id"] = request.user.id
    elif request.session["oidc_mode"] == "login":
        if not request.user.is_anonymous:
            return HttpResponseRedirect(
                request.session["oidc_redirect"] or reverse("user_courses")
            )
    else:
        return HttpResponseBadRequest()

    idp_config = json.loads(requests.get(settings.OIDC_IDP_CONFIGURATION).text)

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
    idp_config = json.loads(requests.get(settings.OIDC_IDP_CONFIGURATION).text)
    code = request.GET.get("code")

    state = request.session.get("oidc_state")
    redirect = request.session.get("oidc_redirect") or reverse("user_courses")
    mode = request.session.get("oidc_mode")
    user_id = request.session.get("oidc_user_id")

    if (
        not code
        or not mode
        or state != request.GET.get("state")
        or (mode == "link" and not user_id)
    ):
        return HttpResponseBadRequest()

    token_response = requests.post(
        idp_config["token_endpoint"],
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.OIDC_REDIRECT_URI,
            "client_id": settings.OIDC_CLIENT_ID,
            "client_secret": settings.OIDC_CLIENT_SECRET,
        },
    )

    if token_response.status_code != 200:
        return HttpResponseServerError()

    access_token = token_response.json().get("access_token")
    if not access_token:
        return HttpResponseServerError()

    userinfo_response = requests.get(
        idp_config["userinfo_endpoint"],
        headers={"Authorization": f"Bearer {access_token}"},
    )

    if userinfo_response.status_code != 200:
        return HttpResponseServerError()

    userinfo = json.loads(userinfo_response.text)
    # return JsonResponse(userinfo)

    if mode == "login":
        # check if user is already logged in
        if not request.user.is_anonymous:
            return HttpResponseRedirect(redirect)
        try:
            switch_data = SwitchData.objects.get(
                swiss_edu_person_unique_id=userinfo["swissEduPersonUniqueID"]
            )
            user = switch_data.user_profile.user
        except SwitchData.DoesNotExist:
            switch_data = SwitchData(
                swiss_edu_person_unique_id=userinfo["swissEduPersonUniqueID"]
            )
            email_query = Q()
            for email in list(
                set(
                    [userinfo["email"]]
                    + userinfo["swissEduIDLinkedAffiliationMail"]
                    + userinfo["swissEduIDAssociatedMail"]
                )
            ):
                email_query |= Q(email__iexact=email)
            email_addresses = EmailAddress.objects.filter(verified=True).filter(
                email_query
            )
            users_with_email = User.objects.filter(pk__in=list(set(email_addresses.values_list("user", flat=True)))).distinct()
            if users_with_email.count() == 1:
                user = users_with_email.get()
                profile = user.profile
            else:
                user = User.objects.create(
                    username=find_unused_username_variant(userinfo["given_name"]),
                    first_name=userinfo["given_name"],
                    last_name=userinfo["family_name"],
                    email=userinfo["email"],
                )
                profile = UserProfile.objects.create(user=user)
                user.emailaddress_set.create(
                    email=userinfo["email"], verified=True
                )
            switch_data.user_profile = profile

    elif mode == "link":
        if request.user.id != user_id:
            return HttpResponseForbidden()

        if SwitchData.objects.filter(
            swiss_edu_person_unique_id=userinfo["swissEduPersonUniqueID"]
        ).exists():
            logout(request)
            mode = "login"
            switch_data = SwitchData.objects.get(
                swiss_edu_person_unique_id=userinfo["swissEduPersonUniqueID"]
            )
            user = SwitchData.objects.get(
                swiss_edu_person_unique_id=userinfo["swissEduPersonUniqueID"]
            ).user_profile.user
        else:
            switch_data = SwitchData(
                swiss_edu_person_unique_id=userinfo["swissEduPersonUniqueID"]
            )
            user = request.user
            switch_data.user_profile = user.profile

    else:
        return HttpResponseBadRequest()

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
            for email in userinfo["swissEduIDLinkedAffiliationMail"]
        ]
    )
    SwitchDataAssociatedEmail.objects.bulk_create(
        [
            SwitchDataAssociatedEmail(switch_data=switch_data, email=email)
            for email in userinfo["swissEduIDAssociatedMail"]
        ]
    )
    SwitchDataAffiliation.objects.bulk_create(
        [
            SwitchDataAffiliation(switch_data=switch_data, affiliation=affiliation)
            for affiliation in userinfo["swissEduIDLinkedAffiliation"]
        ]
    )

    if switch_data.is_student():
        user.profile.student_validity = datetime.date.today() + datetime.timedelta(
            days=180
        )
        user.profile.save()

    if mode == "login":
        perform_login(request, user)

    return HttpResponseRedirect(redirect if mode == "login" else reverse("profile"))
