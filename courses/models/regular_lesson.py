import operator
from datetime import datetime, timedelta, date
from functools import reduce
from typing import Iterable

from django.db import models
from pytz import timezone

from . import Weekday, LessonOccurrenceData


class RegularLesson(models.Model):
    course = models.ForeignKey(
        "Course", related_name="regular_lessons", on_delete=models.CASCADE
    )
    weekday = models.CharField(max_length=3, choices=Weekday.CHOICES, default=None)
    time_from = models.TimeField()
    time_to = models.TimeField()

    def get_weekday_number(self) -> int:
        return Weekday.NUMBERS[self.weekday]

    def get_occurrences(self) -> Iterable[LessonOccurrenceData]:
        period = self.course.get_period()
        cancellations = self.course.get_cancellation_dates()

        all_dates_in_period = map(
            lambda offset: period.date_from + timedelta(days=offset),
            range((period.date_to - period.date_from).days + 1),
        )

        def has_date_a_lesson(d: date) -> bool:
            return (
                d.weekday() == Weekday.NUMBERS[self.weekday] and d not in cancellations
            )

        def to_lesson_occurrence(d: date) -> LessonOccurrenceData:
            return LessonOccurrenceData(
                start=datetime.combine(d, self.time_from, timezone("Europe/Zurich")),
                end=datetime.combine(d, self.time_to, timezone("Europe/Zurich")),
            )

        return map(to_lesson_occurrence, filter(has_date_a_lesson, all_dates_in_period))

    def get_total_time(self) -> timedelta:
        return reduce(operator.add, map(lambda l: l.duration, self.get_occurrences()))

    def __str__(self) -> str:
        return (
            f"{Weekday.WEEKDAYS_TRANSLATIONS[self.weekday]}, "
            f'{self.time_from.strftime("%H:%M")} - {self.time_to.strftime("%H:%M")}'
        )
