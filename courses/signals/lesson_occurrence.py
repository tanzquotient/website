from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from courses.models import (
    RegularLesson,
    IrregularLesson,
    Course,
    RegularLessonException,
    Offering, Period, PeriodCancellation
)


@receiver(post_save, sender=Course)
@receiver(post_save, sender=RegularLesson)
@receiver(post_save, sender=RegularLessonException)
@receiver(post_save, sender=IrregularLesson)
@receiver(post_save, sender=Offering)
@receiver(post_save, sender=Period)
@receiver(post_save, sender=PeriodCancellation)
@receiver(post_delete, sender=RegularLesson)
@receiver(post_delete, sender=RegularLessonException)
@receiver(post_delete, sender=IrregularLesson)
def update_lesson_occurrences(sender, instance, **kwargs):
    courses: list[Course]
    if sender == Course:
        courses = [instance]
    elif sender in [RegularLesson, IrregularLesson]:
        courses = [instance.course]
    elif sender == RegularLessonException:
        courses = [instance.regular_lesson.course]
    elif sender in [Offering, Period]:
        courses = list(instance.courses.all())
    elif sender == PeriodCancellation:
        courses = list(instance.period.courses.all())

    for course in courses:
        course.update_lesson_occurrences()
