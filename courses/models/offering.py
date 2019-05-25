from django.db import models
from . import OfferingType


class Offering(models.Model):
    """An offering is a list of courses to be offered in the given period"""

    name = models.CharField(max_length=30, unique=True, blank=False)
    period = models.ForeignKey('Period', blank=True, null=True, on_delete=models.PROTECT)
    type = models.CharField(max_length=3,
                            choices=OfferingType.CHOICES,
                            default=OfferingType.REGULAR)
    type.help_text = 'The type of the offering influences how the offering is displayed.'
    display = models.BooleanField(default=False)
    display.help_text = 'Defines if the courses in this offering should be displayed on the Website.'
    active = models.BooleanField(default=False)
    active.help_text = 'Defines if clients can subscribe to courses in this offering.'

    def is_preview(self):
        return not self.display

    def __str__(self):
        return '{}'.format(self.name)
