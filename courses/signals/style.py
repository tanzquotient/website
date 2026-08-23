from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from courses.models import Course, Style
from courses.services.cache import (
    invalidate_course_detail_cache,
    invalidate_course_list_cache,
)


@receiver(post_save, sender=Style)
@receiver(post_delete, sender=Style)
def style_changed(sender, instance, **kwargs):
    invalidate_course_list_cache()
    course_ids = Course.objects.filter(type__styles=instance).values_list(
        "pk", flat=True
    )
    invalidate_course_detail_cache(course_ids)
