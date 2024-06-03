from django.db import migrations
from courses.models import Course, LessonOccurrence, LessonOccurrenceTeach, Teach


def forwards(apps, schema_editor):
    courses: list[Course] = Course.objects.all()
    courses = [course for course in courses if course.is_over()]
    for course in courses:
        course.update_lesson_occurrences()
        course_lesson_occurrences: list[LessonOccurrence] = course.lesson_occurrences.all()
        for lesson_occurrence in course_lesson_occurrences:
            for teacher in course.get_teachers():
                lesson_occurrence_teach = LessonOccurrenceTeach(lesson_occurrence=lesson_occurrence, teacher=teacher)
                lesson_occurrence_teach.save()
                lesson_occurrence.teachers.add(lesson_occurrence_teach)
            lesson_occurrence.save()


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0030_lessonoccurrence_lessonoccurrenceteach_and_more"),
    ]

    operations = [
        migrations.RunPython(forwards),
    ]

