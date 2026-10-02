from django.db import models


class Source(models.Model):
    description = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.description


class Destination(models.Model):
    url = models.URLField()

    def __str__(self) -> str:
        return self.url


class Visit(models.Model):
    source = models.ForeignKey(
        Source,
        on_delete=models.PROTECT,
        related_name="visits",
    )
    destination = models.ForeignKey(
        Destination,
        on_delete=models.PROTECT,
        related_name="visits",
    )
    visited_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, default="")

    class Meta:
        indexes = [
            models.Index(fields=["source", "destination"]),
        ]
