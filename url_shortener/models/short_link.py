import secrets
import string

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property

TAG_LENGTH = 8


def generate_short_tag() -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(TAG_LENGTH))


class ShortLink(models.Model):
    description = models.CharField(max_length=255, blank=True)
    tag = models.CharField(
        max_length=16, unique=True, editable=False, default=generate_short_tag
    )
    source = models.ForeignKey(
        "Source", on_delete=models.PROTECT, related_name="short_links"
    )
    destination = models.ForeignKey(
        "Destination", on_delete=models.PROTECT, related_name="short_links"
    )
    deactivated = models.BooleanField(
        default=False, verbose_name="Manually deactivated"
    )
    valid_from = models.DateTimeField(blank=True, null=True)
    valid_until = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.tag

    def clean(self):
        if self.valid_from and self.valid_until and self.valid_from > self.valid_until:
            raise ValidationError(
                {"valid_until": "Valid until must not be before valid from."}
            )

    @cached_property
    def has_visits(self) -> bool:
        return self.visits.exists()

    def short_url(self) -> str:
        path = reverse("url_shortener:redirect", kwargs={"tag": self.tag})
        return f"https://{settings.DEPLOYMENT_DOMAIN}{path}"
