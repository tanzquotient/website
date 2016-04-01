from django.db import models
from hvad.models import TranslatableModel, TranslatedFields
from django.conf import settings
import services

QUESTION_TYPES = (('c', u'single choice'), ('cf', u'single choice with free form'), ('m', u'multiple choice'),
                  ('mf', u'multiple choice with free form'), ('s', u'scale'), ('f', u'free form'))


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


class SurveyInstance(models.Model):
    survey = models.ForeignKey('Survey', related_name='survey_instances', blank=False,
                               null=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='survey_instances', blank=False,
                             null=False)
    courses = models.ManyToManyField('courses.Course', related_name='survey_instances', blank=True)
    date = models.DateTimeField(blank=False, null=False, auto_now_add=True)
    url_text = models.CharField(blank=True, null=False, max_length=100, unique=True)
    url_checksum = models.CharField(blank=True, null=False, max_length=12)
    url_expire_date = models.DateTimeField(blank=True, null=True, auto_now_add=False)

    def save(self, *args, **kwargs):
        super(SurveyInstance, self).save(*args, **kwargs)  # save here to ensure id is set by database
        if not self.url_checksum:
            text, checksum = services.encode_data(self.id)
            self.url_text = text
            self.url_checksum = checksum
        print services.create_url(self)
        super(SurveyInstance, self).save(*args, **kwargs)


class Answer(models.Model):
    survey_instance = models.ForeignKey('SurveyInstance', related_name='answers', blank=False, null=True,
                                        on_delete=models.CASCADE)
    question = models.ForeignKey('Question', related_name='answers', blank=False, null=True, on_delete=models.CASCADE)
    choice = models.ForeignKey('Question', blank=True, null=True, on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    value = models.IntegerField(blank=True, null=True)
