from django.db import models
from . import OfferingType
from datetime import date


class Offering(models.Model):
    """An offering is a list of courses to be offered in the given period"""

    name = models.CharField(max_length=30, unique=True, blank=False)
    period = models.ForeignKey('Period', blank=True, null=True, on_delete=models.PROTECT)
    type = models.CharField(max_length=3, choices=OfferingType.CHOICES, default=OfferingType.REGULAR)
    type.help_text = 'The type of the offering influences how the offering is displayed.'
    display = models.BooleanField(default=False)
    display.help_text = 'Defines if the courses in this offering should be displayed on the Website.'
    active = models.BooleanField(default=False)
    active.help_text = 'Defines if clients can subscribe to courses in this offering.'
    preview = models.BooleanField(default=False)
    preview.help_text = 'Defines if the offering should be displayed as preview'

    def is_public(self):
        return self.display or self.is_historic()

    def is_preview(self):
        return self.preview

    def is_historic(self):
        if self.active or self.preview or self.display or not self.has_date_from():
            return False

        return self.period.date_from < date.today()

    def has_date_from(self):
        return self.get_start_year() is not None

    def is_partner_offering(self):
        return self.type == OfferingType.PARTNER

    def get_start_year(self):
        try:
            return self.period.date_from.year
        except:
            return None

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        ordering = ['-period__date_from', 'name']
