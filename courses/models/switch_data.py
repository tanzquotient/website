from django.db import models

from . import UserProfile


class SwitchData(models.Model):
    user_profile = models.OneToOneField(
        UserProfile,
        primary_key=True,
        related_name="switch_data",
        on_delete=models.CASCADE,
    )
    swiss_edu_id = models.CharField(
        max_length=36,
        blank=False,
        verbose_name="swissEduID",
        help_text="Unique person identifier in the Switch edu-ID federation, institution-agnostic.",
        unique=True,
    )
    swiss_edu_person_unique_id = models.CharField(
        max_length=36,
        blank=False,
        verbose_name="swissEduPersonUniqueID",
        help_text="Unique person identifier in the Switch edu-ID federation, institution-aware.",
        unique=True,
    )
    given_name = models.CharField(
        max_length=150,
        blank=False,
        verbose_name="given_name",
        help_text="Given name or first name of the End-User",
    )
    family_name = models.CharField(
        max_length=150,
        blank=False,
        verbose_name="family_name",
        help_text="Surname or last name of the End-User",
    )
    email = models.CharField(
        max_length=256,
        blank=False,
        verbose_name="email_verified",
        help_text="	End-User's preferred e-mail address",
        unique=True,
    )

    def is_student(self) -> bool:
        return any([a.is_student_affiliation() for a in self.affiliations.all()])
