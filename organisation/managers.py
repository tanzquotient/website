from django.db import models

class FunctionManager(models.Manager):
    def active(self):
        return self.all().filter(active=True).order_by("position")

        