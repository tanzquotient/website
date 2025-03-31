from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.utils.functional import cached_property
from django.db import models

from courses import managers
from courses.models import Room, IrregularLesson, RegularLessonException


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

    objects = managers.LessonOccurrenceQuerySet.as_manager()

    @cached_property
    def room(self) -> Room:
        for l in self.course.get_lesson_occurrences():
            if l.start == self.start and l.end == self.end:
                return l.room
        return self.course.room

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
