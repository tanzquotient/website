from django.db import models
from django.utils.translation import gettext_lazy as _
from djangocms_text.fields import HTMLField
from parler.models import TranslatableModel, TranslatedFields

from ..managers import CourseTypeManager


class CourseType(TranslatableModel):
    styles = models.ManyToManyField("Style", related_name="course_types", blank=True)
    level = models.IntegerField(default=None, blank=True, null=True)
    couple_course = models.BooleanField(default=True)
    predecessors = models.ManyToManyField(
        to="CourseType",
        related_name="successors",
        blank=True,
        help_text=_(
            (
                "Course types that allow for early subscription "
                "(within time bounds) to courses if this type."
            )
        ),
    )

    translations = TranslatedFields(
        title=models.CharField(
            verbose_name="[TR] Title",
            max_length=64,
            blank=False,
            help_text="This will be the title shown for all courses of this type.",
        ),
        subtitle=models.CharField(
            verbose_name="[TR] Subtitle",
            max_length=128,
            blank=True,
            null=True,
            help_text="A short teaser, that is displayed below the title for more information.",
        ),
        description=HTMLField(
            verbose_name="[TR] Description",
            blank=True,
            null=True,
            help_text="This text is added to the description of each course instance.",
        ),
        information_for_participants=HTMLField(
            verbose_name="[TR] Information for participants",
            blank=True,
            null=True,
            help_text=_(
                "Shown only to participants of courses of this type on the course page. Cannot be set by teachers in the frontend."
            ),
        ),
    )

    def format_styles(self) -> str:
        return ", ".join(map(str, self.styles.all()))

    format_styles.short_description = "Styles"

    objects = CourseTypeManager()

    def __str__(self) -> str:
        return self.title
