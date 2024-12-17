from django.db.models.signals import post_save, post_delete
from django.db.models import Q
from django.dispatch import receiver
from courses.models import (
    RegularLesson,
    IrregularLesson,
    Course,
    RegularLessonException,
    Offering,
    Period,
    PeriodCancellation,
    LessonOccurrenceTeach,
    RoomCancellation,
)


@receiver(post_save, sender=Course)
@receiver(post_save, sender=RegularLesson)
@receiver(post_save, sender=RegularLessonException)
@receiver(post_save, sender=IrregularLesson)
@receiver(post_save, sender=Offering)
@receiver(post_save, sender=Period)
@receiver(post_save, sender=PeriodCancellation)
@receiver(post_save, sender=RoomCancellation)
@receiver(post_delete, sender=RegularLesson)
@receiver(post_delete, sender=RegularLessonException)
@receiver(post_delete, sender=IrregularLesson)
@receiver(post_delete, sender=PeriodCancellation)
@receiver(post_delete, sender=RoomCancellation)
def update_lesson_occurrences(sender, instance, **kwargs):
    courses: list[Course]
    if sender == Course:
        courses = [instance]
    elif sender in [RegularLesson, IrregularLesson]:
        courses = [instance.course]
    elif sender == RegularLessonException:
        courses = [instance.regular_lesson.course]
    elif sender == Offering:
        courses = list(instance.course_set.all())
    elif sender == Period:
        period_query = Q(period=instance) | Q(offering__period=instance)
        courses = list(Course.objects.filter(period_query).all())
    elif sender == PeriodCancellation:
        courses = list(instance.period.course_set.all())
    elif sender == RoomCancellation:
        courses = list(instance.room.courses.all())

    for course in courses:
        course.update_lesson_occurrences()


@receiver(post_save, sender=LessonOccurrenceTeach)
@receiver(post_delete, sender=LessonOccurrenceTeach)
def update_hourly_wages(sender, instance, **kwargs):
    for l in LessonOccurrenceTeach.objects.filter(
        teacher=instance.teacher,
        lesson_occurrence__start__gt=instance.lesson_occurrence.end,
    ).all():
        l.update_hourly_wage()
