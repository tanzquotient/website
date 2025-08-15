from django.core.validators import MinValueValidator
from django.db.models import CASCADE, Model, ForeignKey, IntegerField


class SkillDanceLevel(Model):
    """
    Used to track who has reached what level for a given dance (style).
    This model is not directly linked to users, but through the Skill model,
    which aggregates all capabilities of a given user.
    """

    skill = ForeignKey("courses.Skill", related_name="dance_levels", on_delete=CASCADE)
    style = ForeignKey("courses.Style", related_name="user_skills", on_delete=CASCADE)
    level = IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = "dance level"
        ordering = "skill", "level", "style"
        unique_together = "skill", "style"

    def __str__(self) -> str:
        return f"{self.skill.user.get_full_name()}: {self.style.name} {self.level}"
