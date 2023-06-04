from __future__ import annotations

from django.db.models import TextField, CharField, BooleanField
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields

from utils import TranslationUtils


class Survey(TranslatableModel):
    name = CharField(max_length=255, blank=False)
    teachers_allowed = BooleanField(
        default=False,
        help_text=_(
            "If set to true, teachers will be able to view the "
            "answers for their courses."
        ),
    )

    translations = TranslatedFields(
        title=CharField(
            verbose_name="[TR] Title", max_length=64, blank=True, null=True
        ),
        intro_text=TextField(verbose_name="[TR] Intro text", blank=True, null=True),
    )

    def copy(self) -> Survey:
        old = Survey.objects.get(pk=self.id)
        self.pk = None
        i = 1
        while True:
            self.name = f"{old.name} (Copy {i})"
            if not Survey.objects.filter(name=self.name).exists():
                break
            i += 1
        self.save()

        TranslationUtils.copy_translations(old, self)

        for question_group in old.questiongroup_set.all():
            question_group.copy(self)

        return self

    def __str__(self) -> str:
        return self.name
