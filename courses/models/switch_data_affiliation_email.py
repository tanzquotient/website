from django.db import models

from . import SwitchData


class SwitchDataAffiliationEmail(models.Model):
    switch_data = models.ForeignKey(
        SwitchData,
        related_name="affiliation_emails",
        on_delete=models.CASCADE,
    )
    email = models.EmailField(
        blank=False,
        max_length=256,
    )
