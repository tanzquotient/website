from django.db.models.signals import post_delete
from django.dispatch import receiver
from courses.models import Subscribe


@receiver(post_delete, sender=Subscribe)
def update_waiting_lists(sender, instance: Subscribe, **kwargs):
    instance.course.update_waiting_list()
