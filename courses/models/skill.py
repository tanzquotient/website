from django.contrib.auth.models import User
from django.db.models import OneToOneField, CASCADE, Model


class Skill(Model):
    """
    We want to store this information, instead of computing it on the fly, to allow
    manually unlocking skills for users.
    E.g. an admin can allow someone who has done dance courses outside Tanzquotient to
    be eligible for e.g. substituting for Ballrom 6
    """

    user = OneToOneField(User, related_name="skill", on_delete=CASCADE)

    def __str__(self) -> str:
        return f"{self.user.get_full_name()} knows {self.dance_levels.count()} dances"

    class Meta:
        ordering = ["user__first_name", "user__last_name"]
