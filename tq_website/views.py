from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic import RedirectView

# TODO: remove after debugging
from django.contrib.auth.decorators import user_passes_test

import requests
from urllib.parse import urlencode
from jose import jwt
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest

import secrets


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


@user_passes_test(lambda u: u.is_superuser)
def openid_connect_login(request: HttpRequest):

    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)

    request.session["oidc_state"] = state
    request.session["oidc_nonce"] = nonce

    params = {
        "client_id": settings.OIDC_CLIENT_ID,
        "response_type": "code",
        "scope": "openid home-organization",
        "redirect_uri": settings.OIDC_REDIRECT_URI,
        "state": state,
        "nonce": nonce,
    }
    url = f"{settings.OIDC_AUTHORIZATION_ENDPOINT}?{urlencode(params)}"
    return HttpResponseRedirect(url)


@user_passes_test(lambda u: u.is_superuser)
def openid_connect_callback(request: HttpRequest):

    state = request.GET.get("state")
    if not state or state != request.session.get("oidc_state"):
        return HttpResponse("Invalid state parameter", status=400)
    request.session.pop("oidc_state", None)

    code = request.GET.get("code")
    if not code:
        return HttpResponse("Missing authorization code", status=400)

    token_response = requests.post(
        settings.OIDC_TOKEN_ENDPOINT,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.OIDC_REDIRECT_URI,
            "client_id": settings.OIDC_CLIENT_ID,
            "client_secret": settings.OIDC_CLIENT_SECRET,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    if token_response.status_code != 200:
        return HttpResponse("Token exchange failed", status=400)

    token_data = token_response.json()
    id_token = token_data.get("id_token")
    if not id_token:
        return HttpResponse("Missing ID token", status=400)

    # Decode ID token
    headers = jwt.get_unverified_header(id_token)
    kid = headers["kid"]
    jwks = requests.get(settings.OIDC_JWKS_ENDPOINT).json()

    key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
    if not key:
        return HttpResponse("Key not found", status=400)

    claims = jwt.decode(
        id_token,
        key=key,
        algorithms=["RS256"],
        audience=settings.OIDC_CLIENT_ID,
        access_token=token_data.get("access_token"),
    )

    if claims.get("nonce") != request.session.get("oidc_nonce"):
        return HttpResponse("Invalid nonce", status=400)
    request.session.pop("oidc_nonce", None)

    affiliation = claims.get("home_organization_affiliation")
    return HttpResponse(f"Authenticated! Affiliation: {affiliation}, claims: {claims}")
