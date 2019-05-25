from django.db import models
from post_office.models import Email


class Confirmation(models.Model):
    subscription = models.ForeignKey('Subscribe', related_name='confirmations', on_delete=models.CASCADE)
    date = models.DateField(blank=False, null=False, auto_now_add=True)
    date.help_text = 'The date when the participation confirmation mail was sent to the subscriber.'
    mail = models.ForeignKey(Email, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return '({}) confirmed at {}'.format(self.subscription, self.date)
