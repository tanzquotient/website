from datetime import datetime, timedelta
from typing import Optional

from django.db import models

from . import Weekday


class RegularLesson(models.Model):
    course = models.ForeignKey('Course', related_name='regular_lessons', on_delete=models.CASCADE)
    weekday = models.CharField(max_length=3, choices=Weekday.CHOICES, default=None)
    time_from = models.TimeField()
    time_to = models.TimeField()

    def get_weekday_number(self) -> int:
        return Weekday.NUMBERS[self.weekday]

    def get_total_time(self) -> Optional[timedelta]:
        period = self.course.get_period()
        if not period or not period.date_from or not period.date_to:
            return None  # time cannot be calculated because period is unknown

        cancellations = self.course.get_cancellation_dates()

        all_days_in_period = \
            (period.date_from + timedelta(x) for x in range((period.date_to - period.date_from).days + 1))

        course_days_in_period = filter(
            lambda date: date.weekday() == Weekday.NUMBERS[self.weekday] and date not in cancellations,
            all_days_in_period
        )

        amount_lessons = len(list(course_days_in_period))

        time_per_lesson = \
            datetime.combine(datetime.today(), self.time_to) - datetime.combine(datetime.today(), self.time_from)

        return amount_lessons * time_per_lesson

    def __str__(self) -> str:
        return "{}, {}, {}-{}".format(self.course, Weekday.WEEKDAYS_TRANSLATIONS_DE[self.weekday],
                                      self.time_from.strftime("%H:%M"),
                                      self.time_to.strftime("%H:%M"))
