from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from courses.models import (
    Subscribe,
    Skill,
    SubscribeState,
)
from courses.utils.skill import skill_utils


@receiver(post_save, sender=User)
def create_skill_on_user_creation(created: bool, instance: User, **kwargs) -> None:
    if created:
        Skill.objects.create(user=instance)


@receiver(post_save, sender=Subscribe)
def update_skill_on_subscribe(instance: Subscribe, **kwargs) -> None:
    if instance.state not in SubscribeState.ACCEPTED_STATES:
        return

    skill, _ = Skill.objects.get_or_create(user=instance.user)
    unlocked_skills = skill.unlocked_course_types.all()
    for course_type in skill_utils.transitive_predecessors(instance.course.type):
        if course_type not in unlocked_skills:
            skill.unlocked_course_types.add(course_type)
