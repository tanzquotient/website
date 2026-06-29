from django.conf import settings
from django.db import models


class RoomAccessCodeView(models.Model):
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="room_code_views",
        null=False,
        blank=False,
    )
    access_code = models.ForeignKey(
        to="courses.RoomAccessCode",
        on_delete=models.CASCADE,
        related_name="views",
        null=False,
        blank=False,
    )
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.user} viewed {self.access_code} at {self.viewed_at:%d.%m.%Y %H:%M}"
        )

    class Meta:
        verbose_name = "room access code view"
        verbose_name_plural = "room access code views"
        ordering = ["-viewed_at"]
