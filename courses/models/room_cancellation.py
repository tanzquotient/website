from django.db import models


class RoomCancellation(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    name.help_text = "Recommended. Makes identifying the cancellation easier."
    room = models.ForeignKey(
        "Room", related_name="cancellations", on_delete=models.CASCADE
    )
    date = models.DateField(blank=False)

    def __str__(self):
        room_date_string = "{}, {}".format(self.room, self.date.strftime("%d.%m.%Y"))
        if self.name:
            return "{} ({})".format(self.name, room_date_string)
        return room_date_string

    class Meta:
        ordering = ["-date"]
