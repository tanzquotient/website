from django.db import models


class Destination(models.Model):
    url = models.URLField()
    label = models.CharField(blank=True)

    def __str__(self) -> str:
        return self.label or self.url
