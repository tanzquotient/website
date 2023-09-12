from datetime import date, timedelta

from django.db.models import (
    Model,
    CharField,
    DateTimeField,
    DurationField,
)


class RegistrationPeriod(Model):
    name = CharField(max_length=30, unique=True, blank=False)
    start = DateTimeField(
        help_text="People will be able to sign up for courses, starting with this "
        "point in time.",
    )
    deadline = DurationField(
        default=timedelta(hours=-12),
        help_text="The registration deadline is relative to the start of the first "
        "lesson. A negative value means, the registration deadline is before the "
        "first lesson. If you for example want to allow sign-ups until the second "
        "week, you can set this value to 7 days.",
    )
    preregistration = DurationField(
        default=timedelta(hours=24),
        help_text="People eligible for preregistration (e.g. participants of a "
        "preceding course) are allowed to sign up this much before the general "
        "registration starts.",
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["name"]
