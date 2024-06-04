from decimal import Decimal

from django.db import models
from django.contrib.auth.models import User

from courses.models import Teach


class LessonOccurrenceTeach(models.Model):
    lesson_occurrence = models.ForeignKey(to="LessonOccurrence", on_delete=models.CASCADE)
    teacher = models.ForeignKey(to=User, on_delete=models.CASCADE)
    hourly_wage = models.DecimalField(
        blank=True,
        null=True,
        decimal_places=2,
        max_digits=6,
    )

    def save(self, *args, **kwargs) -> None:
        if self.hourly_wage is None:
            self.hourly_wage = self.calculate_hourly_wage()
        super(LessonOccurrenceTeach, self).save(*args, **kwargs)

    def calculate_hourly_wage(self) -> Decimal:
        # For external courses, teachers are not paid by us
        if self.lesson_occurrence.course.is_external():
            return Decimal(0)
        # Compute the hourly wage
        else:
            return self.teacher.profile.get_hourly_wage()

    class Meta:
        unique_together = (('lesson_occurrence', 'teacher'),)