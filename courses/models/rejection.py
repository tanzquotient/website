from django.db import models
from . import RejectionReason
from post_office.models import Email


class Rejection(models.Model):
    subscription = models.ForeignKey(
        "Subscribe", related_name="rejections", on_delete=models.CASCADE
    )
    date = models.DateField(blank=False, null=False, auto_now_add=True)
    date.help_text = "The date when the rejection mail was sent to the subscriber."
    reason = models.CharField(
        max_length=30,
        choices=RejectionReason.CHOICES,
        blank=False,
        null=False,
        default=RejectionReason.UNKNOWN,
    )
    mail_sent = models.BooleanField(blank=False, null=False, default=True)
    mail_sent.help_text = "If this rejection was communicated to user by email."
    mail = models.ForeignKey(Email, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return "({}) rejected at {}".format(self.subscription, self.date)
