from django.db import models

from . import SwitchData


class SwitchDataAssociatedEmail(models.Model):
    switch_data = models.ForeignKey(
        SwitchData,
        related_name="associated_emails",
        on_delete=models.CASCADE,
    )
    email = models.EmailField(
        blank=False,
        max_length=256,
    )
