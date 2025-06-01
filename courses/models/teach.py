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
    hourly_wage = models.DecimalField(
        blank=True,
        null=True,
        decimal_places=2,
        max_digits=6,
        help_text="Leave empty (not 0!) to follow TQ standard wage scheme"
    )

    def __str__(self) -> str:
        return f"{self.teacher} teaches {self.course}"
