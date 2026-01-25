from decimal import Decimal
from post_office.models import STATUS

from django.contrib.auth.models import User
from django.db import models
from courses.models import TeacherWelcome


class Teach(models.Model):
    teacher = models.ForeignKey(
        User, related_name="teaching_courses", on_delete=models.CASCADE
    )
    course = models.ForeignKey(
        "Course", related_name="teaching", on_delete=models.CASCADE
    )
    hourly_wage = models.DecimalField(
        blank=True,
        null=True,
        decimal_places=2,
        max_digits=6,
        help_text="Leave empty (not 0!) to follow TQ standard wage scheme",
    )

    def __str__(self) -> str:
        return f"{self.teacher} teaches {self.course}"

    @property
    def welcomed(self) -> bool:
        return TeacherWelcome.objects.filter(
            teach=self, mail__status=STATUS.sent
        ).exists()
