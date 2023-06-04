from django.contrib.auth.models import User
from django.db import models


class TeachLesson(models.Model):
    teacher = models.ForeignKey(
        User, related_name="teaching_lessons", on_delete=models.CASCADE
    )
    lesson = models.ForeignKey(
        "LessonDetails", related_name="teaching", on_delete=models.CASCADE
    )
    hourly_wage = models.DecimalField(
        blank=True, null=True, decimal_places=2, max_digits=6
    )
    hourly_wage.help_text = (
        "Hourly wage, leave empty to copy default wage from teacher profile."
    )

    def __str__(self) -> str:
        return "{} teaches {}".format(self.teacher, self.lesson)
