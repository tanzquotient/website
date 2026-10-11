import base64
import binascii
import hmac
from functools import wraps

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.http import HttpResponse, HttpResponseNotFound
from django.views.generic import RedirectView


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
