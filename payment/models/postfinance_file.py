from django.db import models

from tq_website.settings import postfinance_file_storage


class PostfinanceFile(models.Model):
    name = models.CharField(max_length=200, unique=True, blank=False, null=False)
    file = models.FileField(blank=False, null=False, storage=postfinance_file_storage())
    processed = models.BooleanField(default=False, null=False, blank=False)
    downloaded_at = models.DateTimeField(null=False, blank=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-downloaded_at']
