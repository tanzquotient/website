from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q


class RoomAccessCode(models.Model):

    class DisplayFormat(models.TextChoices):
        PLAIN = "plain"
        QR_CODE = "qr"

    class Visibility(models.TextChoices):
        PUBLIC = "public"
        PARTICIPANTS = "participants"
        TEACHERS = "teachers"
        STAFF = "staff"

    room = models.ForeignKey(
        to="courses.Room",
        on_delete=models.CASCADE,
        related_name="access_codes",
    )
    valid_from = models.DateField(
        help_text="From when the access code is valid (inclusive)"
    )
    valid_until = models.DateField(
        help_text="Until when the access code is valid (inclusive)"
    )
    code = models.CharField(max_length=1000)
    display_format = models.CharField(max_length=5, choices=DisplayFormat.choices)
    visibility = models.CharField(max_length=12, choices=Visibility.choices)

    def clean(self, *args, **kwargs):
        if self.valid_from and self.valid_until and self.valid_from > self.valid_until:
            error_message = "Valid from date cannot be after valid until date."
            raise ValidationError(
                {
                    "valid_from": error_message,
                    "valid_until": error_message,
                }
            )

        overlap_condition = Q(valid_from__lte=self.valid_until) & Q(
            valid_until__gte=self.valid_from
        )

        conflicting_codes = RoomAccessCode.objects.filter(room=self.room).filter(
            overlap_condition
        )

        if self.pk:
            conflicting_codes = conflicting_codes.exclude(pk=self.pk)

        if conflicting_codes.exists():
            error_message = (
                "An existing access code is already valid "
                "during this period for this room."
            )

            raise ValidationError(
                {
                    "valid_from": error_message,
                    "valid_until": error_message,
                }
            )
