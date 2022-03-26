from __future__ import annotations

from django.db.models import CharField, ForeignKey, BooleanField, PositiveSmallIntegerField, TextField, PROTECT
from parler.models import TranslatableModel, TranslatedFields

from utils import TranslationUtils
from .types import QuestionType


class Question(TranslatableModel):
    name = CharField(max_length=255)
    question_group = ForeignKey('QuestionGroup', blank=False, null=True, on_delete=PROTECT)
    type = CharField(max_length=3, choices=QuestionType.CHOICES, default=QuestionType.FREE_FORM)
    scale = ForeignKey('Scale', blank=True, null=True, on_delete=PROTECT,
                       help_text='Only needed for question type "choice"')
    display = BooleanField(default=True, help_text="Defines if this question is displayed in survey; "
                                                   "set this to false instead of deleting")
    position = PositiveSmallIntegerField("Position", default=0)

    translations = TranslatedFields(
        text=TextField(verbose_name='[TR] Text', blank=True, null=True),
        note=TextField(verbose_name='[TR] Note', blank=True, null=True),
    )

    def copy(self, question_group) -> Question:
        old = Question.objects.get(pk=self.id)
        self.pk = None
        self.question_group = question_group
        self.save()

        TranslationUtils.copy_translations(old, self)

        for choice in old.choice_set.all():
            choice.copy(self)

        return self

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ['position']
        unique_together = ['name', 'question_group']
