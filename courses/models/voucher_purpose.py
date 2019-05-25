from django.db import models


class VoucherPurpose(models.Model):
    name = models.CharField(max_length=255, unique=True, blank=False)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
