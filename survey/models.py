from django.db import models
from hvad.models import TranslatableModel, TranslatedFields
from django.conf import settings

QUESTION_TYPES = (('c', u'single choice'), ('m', u'multiple choice'), ('s', u'scale'), ('f', u'free form'))


class Survey(TranslatableModel):
    name = models.CharField(max_length=255, blank=False)

    translations = TranslatedFields(
        intro_text=models.TextField(blank=True, null=True),
    )

    def __unicode__(self):
        return self.name


class QuestionGroup(TranslatableModel):
    name = models.CharField(max_length=255, unique=True)
    survey = models.ForeignKey('Survey', blank=False, null=True, on_delete=models.SET_NULL)
    position = models.PositiveSmallIntegerField("Position", default=0)

    translations = TranslatedFields(
        intro_text=models.TextField(blank=True, null=True),
    )

    class Meta:
        ordering = ['position']

    def __unicode__(self):
        return self.name


class Question(TranslatableModel):
    name = models.CharField(max_length=255, unique=True)
    question_group = models.ForeignKey('QuestionGroup', blank=False, null=True, on_delete=models.SET_NULL)
    type = models.CharField(max_length=3,
                            choices=QUESTION_TYPES,
                            default='c')
    display = models.BooleanField(default=True)
    display.help_text = "Defines if this question is displayed in survey; set this to false instead of deleting"
    position = models.PositiveSmallIntegerField("Position", default=0)

    translations = TranslatedFields(
        text=models.TextField(blank=True, null=True),
        note=models.TextField(blank=True, null=True),
    )

    class Meta:
        ordering = ['position']

    def __unicode__(self):
        return self.name


class Choice(TranslatableModel):
    question = models.ForeignKey('Question', blank=False, null=True, on_delete=models.CASCADE)
    position = models.PositiveSmallIntegerField("Position", default=0)

    translations = TranslatedFields(
        label=models.CharField(max_length=255)
    )

    class Meta:
        ordering = ['position']


class Answer(models.Model):
    choice = models.ForeignKey('Question', blank=False, null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='survey_answers', blank=False,
                             null=False)
    text = models.TextField(blank=True, null=True)
    value = models.IntegerField(blank=True, null=True)
