from django import template
from django.contrib.auth.models import User

from courses.models import LessonOccurrence, Course, LessonOccurrenceData

register = template.Library()


@register.filter(name="get_lesson_teachers")
def get_lesson_teachers(
    course: Course, lesson_data: LessonOccurrenceData
) -> list[User] | None:
    presence = LessonOccurrence.objects.filter(
        course=course, start=lesson_data.start, end=lesson_data.end
    )
    teachers: list[User | None] = []
    if presence.exists():
        teachers = list(presence.first().teachers.all())
    return teachers + [None for _ in range(len(course.get_teachers()) - len(teachers))]
