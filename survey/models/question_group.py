from __future__ import annotations

from django.db.models import (
    CharField,
    ForeignKey,
    PositiveSmallIntegerField,
    TextField,
    SET_NULL,
)
from parler.models import TranslatableModel, TranslatedFields

from . import Survey
from utils import TranslationUtils


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
