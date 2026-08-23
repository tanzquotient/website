from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from courses.models import Teach
from courses.services.cache import invalidate_course_detail_cache
from tq_website.tasks import task_delete_user_and_courses_calendar_cache


@receiver(post_save, sender=Teach)
@receiver(post_delete, sender=Teach)
def teach_changed(sender, instance: Teach, **kwargs):
    user_ids = list(instance.course.subscriptions.values_list("user", flat=True))
    user_ids += list(instance.course.teaching.values_list("teacher", flat=True))
    task_delete_user_and_courses_calendar_cache.delay(
        user_ids=user_ids,
        course_ids=[instance.course_id],
    )
    invalidate_course_detail_cache([instance.course_id])
