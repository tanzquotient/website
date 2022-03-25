from __future__ import annotations

from django.db.models import TextField, CharField
from django.urls import reverse
from parler.models import TranslatableModel, TranslatedFields

from utils import TranslationUtils


class Survey(TranslatableModel):
    name = CharField(max_length=255, blank=False)

    translations = TranslatedFields(
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
            self.name = old.name + "(Copy {})".format(i)
            if not Survey.objects.filter(name=self.name).exists():
                break
            i += 1
        self.save()

        TranslationUtils.copy_translations(old, self)

        for qg in old.questiongroup_set.all():
            qg.copy(self)

        return self

    def __str__(self) -> str:
        return self.name
