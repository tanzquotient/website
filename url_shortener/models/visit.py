from django.db import models


class Visit(models.Model):
    short_link = models.ForeignKey(
        "ShortLink",
        on_delete=models.PROTECT,
        related_name="visits",
        # Lookups by short link are covered by the (short_link, visited_at) index
        db_index=False,
    )
    visited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["visited_at"]),
            models.Index(fields=["short_link", "visited_at"]),
        ]
