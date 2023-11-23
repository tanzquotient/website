from django.db import models


class PeriodCancellation(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    name.help_text = "Recommended. Makes identifying the cancellation easier. E.g. Monday after Easter"
    period = models.ForeignKey(
        "Period", related_name="cancellations", on_delete=models.CASCADE
    )
    date = models.DateField(blank=False, null=False)

    def __str__(self):
        date_string = "{}".format(self.date.strftime("%d.%m.%Y"))
        if self.name:
            return "{} ({})".format(self.name, date_string)
        return date_string
