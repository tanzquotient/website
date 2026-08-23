from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from courses.models import LessonOccurrence, Room
from courses.services.cache import (
    invalidate_course_detail_cache,
    invalidate_course_list_cache,
)


@receiver(post_save, sender=Room)
@receiver(post_delete, sender=Room)
def room_changed(sender, instance, **kwargs):
    invalidate_course_list_cache()
    course_ids = set(instance.courses.values_list("pk", flat=True))
    course_ids.update(
        LessonOccurrence.objects.filter(room=instance).values_list(
            "course_id", flat=True
        )
    )
    invalidate_course_detail_cache(course_ids)
