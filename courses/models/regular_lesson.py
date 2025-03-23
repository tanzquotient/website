import operator
from datetime import datetime, timedelta, date, time
from functools import reduce
from typing import Iterable

from django.db import models
from pytz import timezone

from . import Weekday, LessonOccurrenceData, Room


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
        period_cancellations = [p.date for p in period.cancellations.all()]

        all_dates_in_period = map(
            lambda offset: period.date_from + timedelta(days=offset),
            range((period.date_to - period.date_from).days + 1),
        )

        def has_date_a_lesson(d: date) -> bool:
            return (
                d.weekday() == Weekday.NUMBERS[self.weekday]
                and d not in period_cancellations
            )

        def to_lesson_occurrence(
            d: date, time_from: time | None = None, time_to: time | None = None, room: Room | None = None,
        ) -> LessonOccurrenceData:
            return LessonOccurrenceData(
                timezone("Europe/Zurich").localize(
                    datetime.combine(d, time_from or self.time_from)
                ),
                timezone("Europe/Zurich").localize(
                    datetime.combine(d, time_to or self.time_to)
                ),
                room or self.course.room,
            )

        lesson_occurrences = []
        for lesson_date in filter(has_date_a_lesson, all_dates_in_period):
            if self.exceptions.filter(date=lesson_date).exists():
                exception = self.exceptions.get(date=lesson_date)
                if exception.is_cancelled():
                    continue
                lesson_occurrences.append(
                    to_lesson_occurrence(
                        lesson_date,
                        exception.get_time_from(),
                        exception.get_time_to(),
                        exception.get_room(),
                    )
                )
            else:
                if self.course.room.is_cancelled(lesson_date):
                    continue
                lesson_occurrences.append(to_lesson_occurrence(lesson_date))

        return lesson_occurrences

    def get_total_time(self) -> timedelta:
        return reduce(operator.add, map(lambda l: l.duration, self.get_occurrences()))

    def __str__(self) -> str:
        return (
            f"{Weekday.WEEKDAYS_TRANSLATIONS[self.weekday]}, "
            f'{self.time_from.strftime("%H:%M")} - {self.time_to.strftime("%H:%M")}'
        )
