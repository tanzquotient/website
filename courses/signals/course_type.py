from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from courses.models import CourseType
from tq_website.tasks import task_delete_user_and_courses_calendar_cache


@receiver(post_save, sender=CourseType)
@receiver(post_delete, sender=CourseType)
def trigger_calendar_cache_delete_from_course_type(
    sender, instance: CourseType, **kwargs
):
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
