import secrets
import string

from django.conf import settings
from django.db import models


def generate_short_tag() -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(16))


class Source(models.Model):
    description = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.description


class Destination(models.Model):
    url = models.URLField()

    def __str__(self) -> str:
        return self.url


class ShortLink(models.Model):
    tag = models.CharField(
        max_length=16, unique=True, editable=False, default=generate_short_tag
    )
    source = models.ForeignKey(
        Source, on_delete=models.PROTECT, related_name="short_links"
    )
    destination = models.ForeignKey(
        Destination, on_delete=models.PROTECT, related_name="short_links"
    )
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.tag


class Visit(models.Model):
    short_link = models.ForeignKey(
        ShortLink,
        on_delete=models.PROTECT,
        related_name="visits",
    )
    visited_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="url_shortener_visits",
    )
