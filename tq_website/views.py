from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic import RedirectView


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
