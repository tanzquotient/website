from django.db import models


class Destination(models.Model):
    url = models.URLField()

    def __str__(self) -> str:
        return self.url
