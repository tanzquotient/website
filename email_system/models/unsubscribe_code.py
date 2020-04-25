from datetime import datetime
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import ForeignKey, DateTimeField, CharField, Model, CASCADE
from django.urls import reverse

def _generate_code():
    return str(uuid4())

class UnsubscribeCode(Model):
    user = ForeignKey(to=User, related_name='unsubscribe_codes', on_delete=CASCADE, blank=False)
    code = CharField(max_length=36, default=_generate_code, blank=False)
    generated_at = DateTimeField(default=datetime.now, blank=False)

    def get_unsubscribe_url(self, context):
        url = reverse('email_system:unsubscribe', kwargs={
            'context': context,
            'user_id': self.user.id,
            'code': self.code
        })
        return 'https://{}{}'.format(settings.DEPLOYMENT_DOMAIN, url)

    def __str__(self):
        return self.code
