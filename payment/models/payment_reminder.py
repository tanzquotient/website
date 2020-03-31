from django.db import models
from post_office.models import Email

from courses.models import Subscribe


class PaymentReminder(models.Model):
    subscription = models.ForeignKey(Subscribe, related_name='payment_reminders', on_delete=models.CASCADE)
    date = models.DateField(blank=False, null=False, auto_now_add=True)
    date.help_text = "The date when the reminder mail was sent to the subscriber."
    mail = models.ForeignKey(Email, blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return "({}) reminded of missing payment at {}".format(self.subscription, self.date)