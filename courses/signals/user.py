from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from courses.models import UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance: User, created: bool, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
