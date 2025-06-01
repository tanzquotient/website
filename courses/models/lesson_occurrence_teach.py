from decimal import Decimal

from django.db import models
from django.contrib.auth.models import User

from courses.models import Teach


class LessonOccurrenceTeach(models.Model):

    lesson_occurrence = models.ForeignKey(
        to="LessonOccurrence", on_delete=models.CASCADE
    )
    teacher = models.ForeignKey(to=User, on_delete=models.CASCADE)
    hourly_wage = models.DecimalField(
        blank=False,
        decimal_places=2,
        max_digits=6,
    )

    def save(self, *args, **kwargs):
        if self.hourly_wage is None:
            self.hourly_wage = self.calculate_hourly_wage()
        super(LessonOccurrenceTeach, self).save(*args, **kwargs)

    def calculate_hourly_wage(self) -> Decimal:
        # For external courses, teachers are not paid by us
        if self.lesson_occurrence.course.is_external():
            return Decimal(0)
        # If the teacher wage for the course is defined, use it
        main_teach = self.lesson_occurrence.course.teaching.filter(teacher=self.teacher)
        # Check if the teacher is not a replacement (if so, follow standard scheme)
        if main_teach.exists():
            course_hourly_wage = main_teach.get().hourly_wage
            if course_hourly_wage is not None:
                return course_hourly_wage  
        # Else, compute the hourly wage based on hours taught
        # or fixed hourly wage as per profile
        return self.teacher.profile.get_hourly_wage(
            until=self.lesson_occurrence.start
        )

    def update_hourly_wage(self) -> None:
        self.hourly_wage = self.calculate_hourly_wage()
        self.save()

    def get_wage(self) -> Decimal:
        hours = self.lesson_occurrence.get_hours()
        return hours * self.hourly_wage

    class Meta:
        unique_together = (("lesson_occurrence", "teacher"),)
