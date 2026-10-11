from django.db import models


class Source(models.Model):
    description = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.description
