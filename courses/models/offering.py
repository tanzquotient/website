from collections import defaultdict
from datetime import date
from decimal import Decimal

from django.utils.translation import gettext_lazy as _
from django.db import models
from parler.models import TranslatableModel, TranslatedFields

from . import OfferingType


class Offering(TranslatableModel):
    """An offering is a list of courses to be offered in the given period"""

    name = models.CharField(max_length=30, unique=True, blank=False, help_text=_("Identifier of the offering. For internal use."))
    translations = TranslatedFields(
        title = models.CharField(max_length=30, blank=True, null=True, verbose_name="[TR] Title", help_text=_("Title of the offering shown to users."))
    )
    period = models.ForeignKey("Period", on_delete=models.PROTECT)
    type = models.CharField(
        max_length=3,
        choices=OfferingType.CHOICES,
        default=OfferingType.REGULAR,
        help_text="The type of the offering influences how the offering is displayed.",
    )
    display = models.BooleanField(
        default=False,
        help_text="Defines if this offering should be displayed on the Website.",
    )
    active = models.BooleanField(
        default=False,
        help_text="Defines if clients can subscribe to courses in this offering.",
    )
    preview = models.BooleanField(
        default=False,
        help_text="Defines if the offering should be displayed as preview",
    )
    opens_soon = models.BooleanField(
        default=False,
        help_text="If set to true, the sign up page says "
        '"opens soon" instead of "closed"',
    )
    group_into_sections = models.BooleanField(
        default=True,
        help_text="If true, a separate section for each month / day of week is "
        "displayed on the course page.",
    )
    limit_courses_per_section = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="If set, only that many courses are shown for each section of the "
        "course list. The remaining courses will be shown when expanding the section.",
    )
    order = models.PositiveSmallIntegerField(
        default=10,
        help_text="Defines how offerings are ordered on the course page. The lower "
        "the number, the further on top.",
    )
    survey = models.ForeignKey(
        "survey.Survey",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        help_text=_(
            "If not empty, will automatically send a survey invitation "
            "to all participants in each course, "
            "as soon as the respective course is over."
        ),
    )

    def is_public(self) -> bool:
        return self.display or self.is_over()

    def is_over(self) -> bool:
        return self.period.date_to < date.today()

    def has_date_from(self) -> bool:
        return self.get_start_year() is not None

    def is_partner_offering(self) -> bool:
        return self.type == OfferingType.PARTNER

    def get_start_year(self) -> int:
        return self.period.date_from.year

    def get_teacher_ids(self) -> set[int]:
        return {
            teaching.teacher_id
            for course in self.course_set.all()
            for teaching in course.teaching.all()
        }

    def payment_totals(self) -> dict[str, Decimal]:
        totals = defaultdict(Decimal)
        for course in self.course_set.all():
            for key, value in course.payment_totals().items():
                totals[key] += value
        return totals
    
    def get_title(self) -> str:
        return self.title if self.title else self.name

    def __str__(self) -> str:
        return "{}".format(self.name)

    class Meta:
        ordering = ["-period__date_to", "name"]
