from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from courses.models import CourseType
from tq_website.tasks import task_delete_user_and_courses_calendar_cache

@receiver(post_save, sender=CourseType)
@receiver(post_delete, sender=CourseType)
def trigger_calendar_cache_delete_from_course_type(sender, instance: CourseType, **kwargs):
    task_delete_user_and_courses_calendar_cache.delay(
        pk=instance.pk,
        sender=sender,
    )