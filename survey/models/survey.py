from __future__ import annotations

from django.db.models import TextField, CharField
from django.urls import reverse
from parler.models import TranslatableModel, TranslatedFields

from utils import TranslationUtils


class Survey(TranslatableModel):
    name = CharField(max_length=255, blank=False)

    translations = TranslatedFields(
        title=CharField(verbose_name='[TR] Title', max_length=64, blank=True, null=True),
        intro_text=TextField(verbose_name='[TR] Intro text', blank=True, null=True),
    )

    def get_test_url(self) -> str:
        return reverse("survey:survey_test", kwargs={'survey_id': self.id})

    get_test_url.short_description = "Test url"

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
