from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from courses.models import Subscribe, Course
from tq_website.tasks import task_delete_user_calendar_cache


@receiver(post_delete, sender=Subscribe)
def update_waiting_lists(sender, instance: Subscribe, **kwargs):
    instance.course.update_waiting_list()

@receiver(post_save, sender=Course)
@receiver(post_delete, sender=Course)
def trigger_calendar_cache_delete_from_course(sender, instance: Course, **kwargs):
    task_delete_user_calendar_cache.delay(
        pk=instance.pk,
        sender=sender,
    )