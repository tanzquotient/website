from datetime import datetime

from django.conf import settings
from django.db import models
from django.db.models import ForeignKey
from django.db.models.fields import DateTimeField
from parler.models import TranslatableModel


class EventParticipant(TranslatableModel):
    user = ForeignKey(settings.AUTH_USER_MODEL, related_name='event_participant', on_delete=models.PROTECT)
    course = ForeignKey('Event', related_name='event_participant', on_delete=models.PROTECT)
    timestamp = DateTimeField(blank=False, null=False, auto_now_add=True)

    def save(self, *args, **kwargs):
        super(EventParticipant, self).save(*args, **kwargs)  # ensure id is set
        if self.timestamp is None:
            self.timestamp = datetime.now()
            super(EventParticipant, self).save(*args, **kwargs)
