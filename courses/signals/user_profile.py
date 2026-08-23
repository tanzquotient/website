from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from courses.models import UserProfile
from courses.services.cache import invalidate_course_detail_cache


@receiver(post_save, sender=UserProfile)
@receiver(post_delete, sender=UserProfile)
def user_profile_changed(sender, instance: UserProfile, **kwargs):
    course_ids = instance.user.teaching_courses.values_list("course_id", flat=True)
    invalidate_course_detail_cache(course_ids)
