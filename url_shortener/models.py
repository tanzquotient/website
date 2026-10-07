import secrets
import string

from django.db import models


def generate_short_tag() -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(8))


class Source(models.Model):
    description = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.description


class Destination(models.Model):
    url = models.URLField()

    def __str__(self) -> str:
        return self.url


class ShortLink(models.Model):
    description = models.CharField(max_length=255, blank=True)
    tag = models.CharField(
        max_length=16, unique=True, editable=False, default=generate_short_tag
    )
    source = models.ForeignKey(
        Source, on_delete=models.PROTECT, related_name="short_links"
    )
    destination = models.ForeignKey(
        Destination, on_delete=models.PROTECT, related_name="short_links"
    )
    deactivated = models.BooleanField(
        default=False, verbose_name="Manually deactivated"
    )
    valid_from = models.DateTimeField(blank=True, null=True)
    valid_until = models.DateTimeField(blank=True, null=True)
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

    class Meta:
        indexes = [
            models.Index(fields=["visited_at"]),
            models.Index(fields=["short_link", "visited_at"]),
        ]
