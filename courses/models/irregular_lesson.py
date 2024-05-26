from datetime import datetime, timedelta
from typing import Iterable

from django.db import models
from django.db.models import CASCADE
from pytz import timezone

from courses.models import LessonOccurrenceData


class IrregularLesson(models.Model):
    course = models.ForeignKey(
        "Course", related_name="irregular_lessons", on_delete=CASCADE
    )
    date = models.DateField(blank=False, null=False)
    time_from = models.TimeField()
    time_to = models.TimeField()

    lesson_details = models.OneToOneField(
        "LessonDetails",
        related_name="irregular_lesson",
        null=True,
        blank=True,
        on_delete=CASCADE,
    )
    lesson_details.help_text = (
        "Only needed, if details are different from course. "
        "E.g. different room, different teachers,..."
    )

    class Meta:
        ordering = ["date", "time_from"]

    def get_occurrence(self) -> LessonOccurrenceData:
        return LessonOccurrenceData(
            timezone("Europe/Zurich").localize(datetime.combine(self.date, self.time_from)),
            timezone("Europe/Zurich").localize(datetime.combine(self.date, self.time_to)),
        )

    def get_occurrences(self) -> Iterable[LessonOccurrenceData]:
        return [self.get_occurrence()]

    def get_total_time(self) -> timedelta:
        return self.get_occurrence().duration

    def format_duration(self) -> str:
        return (
            f"{self.date}, "
            f'{self.time_from.strftime("%H:%M")} - {self.time_to.strftime("%H:%M")}'
        )

    def __str__(self) -> str:
        return self.format_duration()
