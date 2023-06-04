from decimal import Decimal
from typing import Optional

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
        blank=True, null=True, decimal_places=2, max_digits=6
    )
    hourly_wage.help_text = (
        "Hourly wage, leave empty to copy default wage from teacher profile."
    )

    def get_wage(self) -> Optional[Decimal]:
        time = self.course.get_total_time()["total"]
        if time is None or self.hourly_wage is None:
            return None

        return Decimal(time) * self.hourly_wage

    def save(self, *args, **kwargs) -> None:
        if self.hourly_wage is None:
            fixed_wage = self.teacher.profile.fixed_hourly_wage
            default_wage = (
                35 if self.teacher.profile.courses_taught_count() >= 25 else 30
            )
            self.hourly_wage = fixed_wage or default_wage
        super(Teach, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.teacher} teaches {self.course}"
