from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from courses.models import (
    Subscribe,
    Skill,
    SubscribeState,
)
from courses.utils.skill import recompute_dance_levels_for_user


@receiver(post_save, sender=User)
def create_skill_on_user_creation(created: bool, instance: User, **kwargs) -> None:
    if created:
        Skill.objects.create(user=instance)


@receiver(post_save, sender=Subscribe)
def update_skill_on_subscribe(instance: Subscribe, **kwargs) -> None:
    if instance.state not in SubscribeState.ACCEPTED_STATES:
        return

    recompute_dance_levels_for_user(instance.user)
