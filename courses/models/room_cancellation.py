from django.db import models
from datetime import datetime, timedelta, date


class RoomCancellation(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    name.help_text = "Recommended. Makes identifying the cancellation easier."
    room = models.ForeignKey(
        "Room", related_name="cancellations", on_delete=models.CASCADE
    )
    date_from = models.DateTimeField(blank=False)
    date_to = models.DateTimeField(blank=False)

    def get_dates_list(self) -> list[date]:
        return [
            (self.date_from + timedelta(days=i)).date()
            for i in range((self.date_to - self.date_from).days + 1)
        ]

    def __str__(self):
        date_string = "{} - {}".format(
            self.date_from.strftime("%d.%m.%Y %H:%m"),
            self.date_to.strftime("%d.%m.%Y %H:%m"),
        )
        if self.name:
            return "{} ({})".format(self.name, date_string)
        return date_string
