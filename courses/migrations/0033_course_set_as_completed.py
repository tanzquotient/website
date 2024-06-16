from django.db import migrations
from courses.models import Course, LessonOccurrence, LessonOccurrenceTeach, Teach


def set_as_completed(apps, schema_editor):
    courses: list[Course] = Course.objects.all().order_by("period__date_from")
    courses = [course for course in courses if course.is_over_since(days=30)]
    for course in courses:
        course.completed = True
        course.save()


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0032_course_completed"),
    ]

    operations = [
        migrations.RunPython(set_as_completed),
    ]
