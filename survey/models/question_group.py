from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import (
    SET_NULL,
    CharField,
    ForeignKey,
    PositiveSmallIntegerField,
    TextField,
)
from parler.models import TranslatableModel, TranslatedFields

from utils import TranslationUtils

if TYPE_CHECKING:
    from . import Survey


class QuestionGroup(TranslatableModel):
    name = CharField(max_length=255)
    survey = ForeignKey("Survey", blank=True, null=True, on_delete=SET_NULL)
    position = PositiveSmallIntegerField("Position", default=0)

    translations = TranslatedFields(
        title=CharField(
            verbose_name="[TR] Title", max_length=64, blank=True, null=True
        ),
        intro_text=TextField(verbose_name="[TR] Intro text", blank=True, null=True),
    )

    class Meta:
        ordering = ["survey__name", "position"]
        unique_together = (("name", "survey"),)

    def copy(self, survey: Survey) -> QuestionGroup:
        old = QuestionGroup.objects.get(pk=self.id)
        self.pk = None
        self.survey = survey
        self.save()

        TranslationUtils.copy_translations(old, self)

        for question in old.question_set.all():
            question.copy(self)

        return self

    def __str__(self) -> str:
        return self.name
