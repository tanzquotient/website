from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models

from courses import managers
from courses.models import Room


class LessonOccurrence(models.Model):
    course = models.ForeignKey(
        to="Course",
        on_delete=models.CASCADE,
        related_name="lesson_occurrences",
        blank=False,
    )
    start = models.DateTimeField(blank=False)
    end = models.DateTimeField(blank=False)
    teachers = models.ManyToManyField(
        to=User,
        related_name="lesson_occurrences",
        blank=True,
        through="LessonOccurrenceTeach",
    )
    room = models.ForeignKey(
        to=Room,
        blank=False,
        related_name="lesson_occurrences",
        on_delete=models.PROTECT,
    )

    objects = managers.LessonOccurrenceQuerySet.as_manager()

    def duration(self) -> timedelta:
        return self.end - self.start

    def get_hours(self) -> Decimal:
        return Decimal(round(self.duration().total_seconds() / 3600, 2))

    def __str__(self) -> str:
        return f"{self.start} - {self.end}"

    class Meta:
        unique_together = (
            "course",
            "start",
            "end",
        )
        ordering = ["course", "start"]
