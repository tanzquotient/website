from datetime import datetime, time, timedelta

from pytz import timezone

TIMEZONE = timezone("Europe/Zurich")

from courses.models import LessonOccurrence


def change_attendance_deadline(lesson_occurrence: LessonOccurrence) -> datetime:
    return lesson_occurrence.start - timedelta(hours=3)


def claiming_spot_window_open(lesson_occurrence: LessonOccurrence) -> bool:
    lesson_date = lesson_occurrence.start.date()
    claiming_window_start = datetime.combine(lesson_date, time(hour=3), tzinfo=TIMEZONE)
    return datetime.now(tz=TIMEZONE) > claiming_window_start


def change_attendance_window_open(lesson_occurrence: LessonOccurrence) -> bool:
    return datetime.now(tz=TIMEZONE) <= change_attendance_deadline(lesson_occurrence)
