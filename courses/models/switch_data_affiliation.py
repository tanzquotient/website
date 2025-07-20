from django.db import models

from courses.models import SwitchData


class SwitchDataAffiliation(models.Model):
    switch_data = models.ForeignKey(
        SwitchData,
        related_name="affiliations",
        on_delete=models.CASCADE,
    )
    affiliation = models.CharField(
        blank=False,
        max_length=256,
    )

    def is_student_affiliation(self) -> bool:
        return self.affiliation.split("@")[0] == "student"
