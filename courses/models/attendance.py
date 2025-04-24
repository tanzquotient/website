from django.contrib.auth.models import User
from django.db.models import ForeignKey, CharField, Model, CASCADE

from .choices import AttendanceState


class Attendance(Model):
    DEFAULT_STATE = AttendanceState.PRESENT

    user = ForeignKey(to=User, related_name="attendances", on_delete=CASCADE)
    lesson_occurrence = ForeignKey(
        to="LessonOccurrence", related_name="attendances", on_delete=CASCADE
    )
    state = CharField(
        max_length=24,
        blank=False,
        null=False,
        choices=AttendanceState.CHOICES,
        default=DEFAULT_STATE,
    )

    class Meta:
        unique_together = (("lesson_occurrence", "user"),)

    def __str__(self) -> str:
        return (
            f"{self.lesson_occurrence}, {self.user.get_full_name()}: "
            f"{AttendanceState.NAMES[self.state]}"
        )
