from django.db import models


class Period(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    name.help_text = "Recommended. Makes identifying the period easier"
    date_from = models.DateField(help_text="The start date of this period.")
    date_to = models.DateField(help_text="The end date of this period. Can be left empty.")

    def format_date(self, d) -> str:
        return d.strftime('%d. %b %Y')

    format_date.short_description = 'Period from/to'

    def __str__(self) -> str:
        if self.name:
            return "{} ({})".format(self.name, self.date_as_string())
        return self.date_as_string()

    def date_as_string(self) -> str:
        return "{} - {}".format(self.format_date(self.date_from), self.format_date(self.date_to))
