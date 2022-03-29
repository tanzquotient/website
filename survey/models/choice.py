from __future__ import annotations

from django.db import models
from parler.models import TranslatableModel, TranslatedFields

from utils import TranslationUtils


class Choice(TranslatableModel):
    question = models.ForeignKey('Question', blank=False, null=True, on_delete=models.CASCADE)
    position = models.PositiveSmallIntegerField("Position", default=0)
    value = models.CharField(max_length=32)

    translations = TranslatedFields(
        label=models.CharField(verbose_name='[TR] Label', max_length=255)
    )

    def get_question_name(self) -> str:
        return self.question.name

    get_question_name.short_description = "Question Name"

    def copy(self, question) -> Choice:
        old = Choice.objects.get(pk=self.id)
        self.pk = None
        self.question = question
        self.save()
        TranslationUtils.copy_translations(old, self)
        return self

    def __str__(self) -> str:
        return self.value

    class Meta:
        ordering = ['position']
