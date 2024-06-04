from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models


class Teach(models.Model):
    teacher = models.ForeignKey(
        User, related_name="teaching_courses", on_delete=models.CASCADE
    )
    course = models.ForeignKey(
        "Course", related_name="teaching", on_delete=models.CASCADE
    )
    welcomed = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.teacher} teaches {self.course}"
