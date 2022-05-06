from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models import ForeignKey, Model
from django.db.models.fields import DateTimeField


class EventRegistration(Model):
    user = ForeignKey(to=User, related_name='event_registrations', on_delete=models.PROTECT)
    event = ForeignKey('Event', related_name='registrations', on_delete=models.PROTECT)
    timestamp = DateTimeField(blank=False, null=False, auto_now_add=True)

    def save(self, *args, **kwargs):
        super(EventRegistration, self).save(*args, **kwargs)  # ensure id is set
        if self.timestamp is None:
            self.timestamp = datetime.now()
            super(EventRegistration, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('user', 'event')
