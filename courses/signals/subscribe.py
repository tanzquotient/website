from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from courses.models import Subscribe
from tq_website.tasks import task_delete_user_and_courses_calendar_cache

@receiver(post_save, sender=Subscribe)
@receiver(post_delete, sender=Subscribe)
def trigger_calendar_cache_delete_from_subscribe(_sender, instance: Subscribe, **kwargs):
    task_delete_user_and_courses_calendar_cache.delay(
        user_ids=[instance.user_id],
        course_ids=[],
    )