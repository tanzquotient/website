from collections import defaultdict
from datetime import date
from decimal import Decimal
from typing import Optional

from django.db import models

from . import OfferingType


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
    opens_soon = models.BooleanField(default=False,
                                     help_text='If set to true, the sign up page says "opens soon" instead of "closed"')

    def is_public(self) -> bool:
        return self.display or self.is_over()

    def is_over(self) -> bool:
        if not self.period:
            return False  # If there is no period, there is no end date -> not over

        return self.period.date_to < date.today()

    def has_date_from(self) -> bool:
        return self.get_start_year() is not None

    def is_partner_offering(self) -> bool:
        return self.type == OfferingType.PARTNER

    def get_start_year(self) -> Optional[int]:
        return self.period.date_from.year if self.period else None

    def get_teacher_ids(self) -> set[int]:
        return {teaching.teacher_id for course in self.course_set.all() for teaching in course.teaching.all()}

    def payment_totals(self) -> dict[str, Decimal]:
        totals = defaultdict(Decimal)
        for course in self.course_set.all():
            for key, value in course.payment_totals().items():
                totals[key] += value
        return totals

    def __str__(self) -> str:
        return '{}'.format(self.name)

    class Meta:
        ordering = ['-period__date_from', 'name']
