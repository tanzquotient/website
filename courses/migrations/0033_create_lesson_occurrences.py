from django.db import migrations
from courses.models import Course, LessonOccurrence


def forwards(apps, schema_editor):
    courses: list[Course] = Course.objects.all()
    courses = [course for course in courses if course.is_over()]
    for course in courses:
        course.update_lesson_occurrences()
        course_lesson_occurrences: list[LessonOccurrence] = course.lesson_occurrences.all()
        for lesson_occurrence in course_lesson_occurrences:
            for teacher in course.get_teachers():
                lesson_occurrence.teachers.add(teacher)
            lesson_occurrence.save()


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0032_alter_lessonoccurrence_unique_together"),
    ]

    operations = [
        migrations.RunPython(forwards),
    ]
