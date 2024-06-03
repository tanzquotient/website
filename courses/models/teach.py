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
        help_text="Please leave this field empty! The wage is calculated based on "
        "the number of courses taught or the fixed wage set in the teachers profile.",
    )

    def save(self, *args, **kwargs) -> None:
        if self.hourly_wage is None:
            self.hourly_wage = self.calculate_hourly_wage()
        super(Teach, self).save(*args, **kwargs)

    def calculate_hourly_wage(self) -> Decimal:
        # For external courses, teachers are not paid by us
        if self.course.is_external():
            return Decimal(0)
        else:
            return self.teacher.profile.get_hourly_wage()

    def __str__(self) -> str:
        return f"{self.teacher} teaches {self.course}"
