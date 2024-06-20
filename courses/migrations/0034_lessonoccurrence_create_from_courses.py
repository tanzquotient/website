from django.db import migrations
from courses.models import Course, LessonOccurrence, LessonOccurrenceTeach, Teach


def forwards(apps, schema_editor):
    courses: list[Course] = Course.objects.all().order_by("period__date_from")
    courses = [course for course in courses if course.is_over()]
    for course in courses:
        course.update_lesson_occurrences()
        course_lesson_occurrences: list[LessonOccurrence] = (
            course.lesson_occurrences.all()
        )
        for lesson_occurrence in course_lesson_occurrences:
            print(lesson_occurrence.start)
            for teacher in course.get_teachers():
                lesson_occurrence_teach = LessonOccurrenceTeach(
                    lesson_occurrence=lesson_occurrence, teacher=teacher
                )
                lesson_occurrence_teach.save()
            lesson_occurrence.save()


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0033_course_set_as_completed"),
    ]

    operations = [
        migrations.RunPython(forwards),
    ]
