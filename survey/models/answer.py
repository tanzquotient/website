from __future__ import annotations

from django.db.models import Model, TextField, ForeignKey, BooleanField, CASCADE, PROTECT


class Answer(Model):
    survey_instance = ForeignKey('SurveyInstance', related_name='answers', blank=False, null=True, on_delete=CASCADE)
    question = ForeignKey('Question', related_name='answers', blank=False, null=True, on_delete=PROTECT)
    value = TextField(blank=True, null=True)
    hide_from_public_reviews = BooleanField(default=False, help_text="If true, this answer will not be shown publicly.")

    def __str__(self) -> str:
        return self.value or "<not answered>"
