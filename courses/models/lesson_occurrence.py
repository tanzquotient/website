from decimal import Decimal

from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta


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

    def duration(self) -> timedelta:
        return self.end - self.start

    def get_hours(self) -> Decimal:
        return Decimal(round(self.duration().total_seconds() / 3600, 2))

    class Meta:
        unique_together = (
            "course",
            "start",
            "end",
        )
