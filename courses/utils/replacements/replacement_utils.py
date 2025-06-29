from datetime import datetime, time

from pytz import timezone

from courses.models import LessonOccurrence


def change_attendance_deadline(lesson_occurrence: LessonOccurrence) -> datetime:
    lesson_date = lesson_occurrence.start.date()
    return datetime.combine(lesson_date, time(hour=3), tzinfo=timezone("Europe/Zurich"))


def claiming_spot_window_open(lesson_occurrence: LessonOccurrence) -> bool:
    return lesson_occurrence.start > change_attendance_deadline(lesson_occurrence)


def change_attendance_window_open(lesson_occurrence: LessonOccurrence) -> bool:
    return lesson_occurrence.start <= change_attendance_deadline(lesson_occurrence)
