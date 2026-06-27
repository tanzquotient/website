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

    class Meta:
        ordering = ["-viewed_at"]
