from datetime import timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import (
    Model,
    DateTimeField,
    BooleanField,
    ForeignKey,
    CharField,
    PROTECT,
    SET_NULL,
)
from django.urls import reverse
from post_office.models import EmailTemplate
from django.utils import timezone

from utils import CodeGenerator


class SurveyInstance(Model):
    survey = ForeignKey(
        "Survey",
        related_name="survey_instances",
        blank=False,
        null=False,
        on_delete=PROTECT,
    )
    user = ForeignKey(
        User,
        related_name="survey_instances",
        blank=False,
        null=False,
        on_delete=PROTECT,
    )
    email_template = ForeignKey(
        EmailTemplate,
        related_name="survey_instances",
        blank=True,
        null=True,
        on_delete=SET_NULL,
    )
    course = ForeignKey(
        "courses.Course",
        related_name="survey_instances",
        blank=True,
        null=True,
        on_delete=PROTECT,
    )
    date = DateTimeField(blank=False, null=False, auto_now_add=True)
    last_update = DateTimeField(blank=True, null=True, auto_now=True)
    url_expire_date = DateTimeField(blank=False, help_text="If left empty, will default to 90 days after creation.")
    url_key = CharField(
        unique=True,
        default=CodeGenerator.short_uuid,
        blank=False,
        null=False,
        max_length=32,
    )
    is_completed = BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.url_expire_date:
            self.url_expire_date = (self.date or timezone.localdate()) + timedelta(days=90)
        super().save(*args, **kwargs)

    def has_answers(self) -> bool:
        return self.answers.count() > 0

    def get_url(self) -> str:
        return self.create_url()

    def create_url(self) -> str:
        return reverse(
            "survey:survey_with_key",
            kwargs=dict(survey_id=self.survey.id, url_key=self.url_key),
        )

    def create_full_url(self) -> str:
        return f"https://{settings.DEPLOYMENT_DOMAIN}{self.create_url()}"

    def __str__(self) -> str:
        if self.course:
            return "{} for {} of {}".format(self.survey, self.course, self.user)
        else:
            return "{} of {}".format(self.survey, self.user)
