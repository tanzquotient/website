from django import template

from courses.models import AttendanceState, Course, LessonOccurrence
from courses.utils import (
    attendances_by_state,
    course_accepted_subscriptions,
    lesson_lead_follow_balance,
)

register = template.Library()


@register.filter(name="attendance_balance")
def attendance_balance(lesson: LessonOccurrence) -> int:
    return lesson_lead_follow_balance(lesson)


@register.filter(name="attendance_total")
def attendance_total(course: Course) -> int:
    return len(course_accepted_subscriptions(course))


@register.filter(name="attendance_absent")
def attendance_absent(lesson: LessonOccurrence) -> int:
    return len(attendances_by_state(lesson, AttendanceState.ABSENT_STATES))


@register.filter(name="attendance_extra")
def attendance_extra(lesson: LessonOccurrence) -> int:
    return len(attendances_by_state(lesson, [AttendanceState.REPLACEMENT]))
