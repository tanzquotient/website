from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from courses.models import (
    RegularLesson,
    IrregularLesson,
    Course,
    RegularLessonException,
)


@receiver(post_save, sender=Course)
@receiver(post_save, sender=RegularLesson)
@receiver(post_save, sender=RegularLessonException)
@receiver(post_save, sender=IrregularLesson)
@receiver(post_delete, sender=RegularLesson)
@receiver(post_delete, sender=RegularLessonException)
@receiver(post_delete, sender=IrregularLesson)
def update_lesson_occurrences(sender, instance, **kwargs):
    course: Course
    if sender == Course:
        course = instance
    elif sender in [RegularLesson, IrregularLesson]:
        course = instance.course
    elif sender == RegularLessonException:
        course = instance.regular_lesson.course

    course.update_lesson_occurrences()
