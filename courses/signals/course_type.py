from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from courses.models import Course, CourseType
from courses.services.cache import (
    invalidate_course_detail_cache,
    invalidate_course_list_cache,
)
from tq_website.tasks import task_delete_user_and_courses_calendar_cache


@receiver(post_save, sender=CourseType)
@receiver(post_delete, sender=CourseType)
def course_type_changed(sender, instance: CourseType, **kwargs):
    user_ids = []
    course_ids = []
    for course in instance.courses.all():
        user_ids += list(course.subscriptions.values_list("user", flat=True))
        user_ids += list(course.teaching.values_list("teacher", flat=True))
        course_ids.append(course.pk)
    task_delete_user_and_courses_calendar_cache.delay(
        user_ids=user_ids,
        course_ids=course_ids,
    )
    invalidate_course_list_cache()
    invalidate_course_detail_cache(course_ids)


@receiver(m2m_changed, sender=CourseType.styles.through)
def course_type_styles_changed(sender, instance, reverse, **kwargs):
    invalidate_course_list_cache()
    if reverse:
        # instance is a Style; find the CourseTypes it's attached to
        course_ids = Course.objects.filter(
            type__in=instance.course_types.all()
        ).values_list("pk", flat=True)
    else:
        # instance is a CourseType
        course_ids = instance.courses.values_list("pk", flat=True)
    invalidate_course_detail_cache(course_ids)
