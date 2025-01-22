from django.db import models
from djangocms_text.fields import HTMLField
from parler.models import TranslatableModel, TranslatedFields

from . import managers


# Create your models here.
class QuestionGroup(models.Model):
    name = models.CharField(max_length=255, blank=False)

    def __str__(self) -> str:
        return "{}".format(self.name)


class Question(TranslatableModel):
    translations = TranslatedFields(
        question_text=models.TextField(
            verbose_name="[TR] Question text", blank=True, null=True
        ),
        answer_text=HTMLField(verbose_name="[TR] Answer text", blank=True, null=True),
    )

    display = models.BooleanField(default=True)
    question_group = models.ForeignKey(
        "QuestionGroup", related_name="questions", on_delete=models.PROTECT
    )

    # position field for ordering columns (grappelli feature)
    position = models.PositiveSmallIntegerField("Position", default=0)

    class Meta:
        ordering = ["position"]

    objects = managers.QuestionManager()

    def __str__(self) -> str:
        return self.safe_translation_getter("question_text", any_language=True) or "-"
