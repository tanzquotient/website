from django.db import transaction
from django.db.models import Q
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from courses.models import (
    Course,
    IrregularLesson,
    LessonDetails,
    LessonOccurrence,
    LessonOccurrenceTeach,
    Offering,
    Period,
    PeriodCancellation,
    RegularLesson,
    RegularLessonException,
    RoomCancellation,
    Teach,
)
from courses.services.cache import (
    invalidate_course_detail_cache,
    invalidate_course_list_cache,
)
from tq_website.tasks import task_delete_user_and_courses_calendar_cache


def _courses_affected_by_room_cancellation(room_id, cancelled_date) -> Q:
    # include courses that use the room only for some lessons via lesson details
    uses_room = (
        Q(room_id=room_id)
        | Q(irregular_lessons__lesson_details__room_id=room_id)
        | Q(regular_lessons__exceptions__lesson_details__room_id=room_id)
    )
    # only regular lessons within the course period or irregular lessons on that date
    # can fall on the cancelled date, so skip all other (e.g. past) courses
    has_lesson_on_date = (
        Q(period__date_from__lte=cancelled_date, period__date_to__gte=cancelled_date)
        | Q(
            period__isnull=True,
            offering__period__date_from__lte=cancelled_date,
            offering__period__date_to__gte=cancelled_date,
        )
        | Q(irregular_lessons__date=cancelled_date)
    )
    return uses_room & has_lesson_on_date


@receiver(pre_save, sender=RoomCancellation)
def remember_previous_room_cancellation(sender, instance, **kwargs):
    # changing the room or date of a cancellation also affects the old one's courses
    instance._previous_room_and_date = (
        RoomCancellation.objects.filter(pk=instance.pk)
        .values_list("room_id", "date")
        .first()
        if instance.pk
        else None
    )


@receiver(post_save, sender=Course)
@receiver(post_save, sender=RegularLesson)
@receiver(post_save, sender=RegularLessonException)
@receiver(post_save, sender=IrregularLesson)
@receiver(post_save, sender=Offering)
@receiver(post_save, sender=Period)
@receiver(post_save, sender=PeriodCancellation)
@receiver(post_save, sender=RoomCancellation)
@receiver(post_save, sender=LessonDetails)
@receiver(post_delete, sender=Course)
@receiver(post_delete, sender=RegularLesson)
@receiver(post_delete, sender=RegularLessonException)
@receiver(post_delete, sender=IrregularLesson)
@receiver(post_delete, sender=Offering)
@receiver(post_delete, sender=Period)
@receiver(post_delete, sender=PeriodCancellation)
@receiver(post_delete, sender=RoomCancellation)
@receiver(post_delete, sender=LessonDetails)
def schedule_changed(sender, instance, **kwargs):
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
        query = _courses_affected_by_room_cancellation(instance.room_id, instance.date)
        previous = getattr(instance, "_previous_room_and_date", None)
        if previous and previous != (instance.room_id, instance.date):
            query |= _courses_affected_by_room_cancellation(*previous)
        courses = list(Course.objects.filter(query).distinct())
    elif sender == LessonDetails:
        courses = [instance.get_lesson.course] if not kwargs["created"] else []

    # reload the courses instead of using the signal's instances
    # those may hold stale prefetched lessons
    for course in Course.objects.filter(pk__in=[c.pk for c in courses]):
        course.update_lesson_occurrences()

    invalidate_course_list_cache()
    invalidate_course_detail_cache([c.pk for c in courses])


@receiver(post_save, sender=LessonOccurrenceTeach)
@receiver(post_save, sender=Teach)
@receiver(post_delete, sender=LessonOccurrenceTeach)
@receiver(post_delete, sender=Teach)
def update_hourly_wages(sender, instance, **kwargs):
    if sender == LessonOccurrenceTeach:
        for l in LessonOccurrenceTeach.objects.filter(
            teacher=instance.teacher,
            lesson_occurrence__start__gt=instance.lesson_occurrence.end,
        ).all():
            l.update_hourly_wage()

    elif sender == Teach:
        for l in LessonOccurrenceTeach.objects.filter(
            teacher=instance.teacher,
            lesson_occurrence__course=instance.course,
        ).all():
            l.update_hourly_wage()


@receiver(post_save, sender=LessonOccurrence)
@receiver(post_delete, sender=LessonOccurrence)
def lesson_occurrence_changed(sender, instance, **kwargs):
    user_ids = list(instance.course.subscriptions.values_list("user", flat=True))
    user_ids += list(instance.course.teaching.values_list("teacher", flat=True))
    course_id = instance.course_id
    transaction.on_commit(
        lambda: task_delete_user_and_courses_calendar_cache.delay(
            user_ids=user_ids,
            course_ids=[course_id],
        )
    )
    invalidate_course_list_cache()
    invalidate_course_detail_cache([course_id])
