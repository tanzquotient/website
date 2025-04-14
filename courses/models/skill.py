from django.contrib.auth.models import User
from django.db.models import OneToOneField, CASCADE, ManyToManyField, Model
from django.utils.translation import gettext_lazy as _


class Skill(Model):
    """
    We want to store this information, instead of computing it on the fly, to allow
    manually unlocking skills for users.
    E.g. an admin can allow someone who has done dance courses outside Tanzquotient to
    be eligible for e.g. substituting for Ballrom 6
    """

    user = OneToOneField(User, related_name="skill", on_delete=CASCADE)
    unlocked_course_types = ManyToManyField(
        "CourseType",
        related_name="skills",
        help_text=_(
            "Course types which this user has unlocked. "
            "For example, participating Ballroom 5 unlocks Ballroom 1-5. "
            "This information can be used for checking whether prerequisites are met, "
            "i.e for participating in an advanced course, or substituting for a lesson."
        ),
    )

    def __str__(self) -> str:
        return (
            f"{self.user.get_full_name()} has "
            f"{self.unlocked_course_types.count()} unlocked course types"
        )
