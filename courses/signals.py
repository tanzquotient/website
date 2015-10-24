from django.db.models.signals import post_save
from django.dispatch import receiver
import courses.models as my_models
import services

import logging

# Get an instance of a logger
logger = logging.getLogger('tq')


@receiver(post_save, sender=my_models.Subscribe)
def subscription_edit_handler(sender, **kwargs):
    subscription = kwargs.get('instance')
    services.confirm_subscription(subscription)
    services.reject_subscription(subscription)
