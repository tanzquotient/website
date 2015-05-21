from django.db import models


class QuestionManager(models.Manager):
    def displayed(self):
        return self.all().filter(display=True).order_by("position")
