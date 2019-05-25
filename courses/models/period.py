from django.db import models


class Period(models.Model):
    date_from = models.DateField(blank=True, null=True)
    date_from.help_text = "The start date of this period. Can be left empty."
    date_to = models.DateField(blank=True, null=True)
    date_to.help_text = "The end date of this period. Can be left empty. " \
                        "If both are left empty, this period is displayed as 'on request'."

    def format_date(self, d):
        return d.strftime('%d. %b %Y')

    format_date.short_description = 'Period from/to'

    def __str__(self):
        if self.date_from and self.date_to:
            return "{} - {}".format(self.format_date(self.date_from), self.format_date(self.date_to))
        elif self.date_from:
            return "from {}".format(self.format_date(self.date_from))
        elif self.date_to:
            return "to {}".format(self.format_date(self.date_to))
        else:
            return "no restriction"
