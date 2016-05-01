from django.db import models
from parler.models import TranslatableModel, TranslatedFields
from django.conf import settings
import services
from django.shortcuts import get_object_or_404


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
    class Type:
        SINGLE_CHOICE = 'c'
        SINGLE_CHOICE_WITH_FREE_FORM = 'cf'
        MULTIPLE_CHOICE = 'm'
        MULTIPLE_CHOICE_WITH_FREE_FORM = 'mf'
        SCALE = 's'
        FREE_FORM = 'f'

        CHOICES = ((SINGLE_CHOICE, u'single choice'),
                   (SINGLE_CHOICE_WITH_FREE_FORM, u'single choice with free form'),
                   (MULTIPLE_CHOICE, u'multiple choice'),
                   (MULTIPLE_CHOICE_WITH_FREE_FORM, u'multiple choice with free form'),
                   (SCALE, u'scale'),
                   (FREE_FORM, u'free form'))

    name = models.CharField(max_length=255, unique=True)
    question_group = models.ForeignKey('QuestionGroup', blank=False, null=True, on_delete=models.SET_NULL)
    type = models.CharField(max_length=3,
                            choices=Type.CHOICES,
                            default=Type.FREE_FORM)
    scale_template = models.ForeignKey('ScaleTemplate', blank=True, null=True, on_delete=models.SET_NULL)
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


class ScaleTemplate(TranslatableModel):
    translations = TranslatedFields(
        low=models.CharField(max_length=30),
        mid=models.CharField(max_length=30, blank=True, null=True),
        up=models.CharField(max_length=30)
    )

    def __unicode__(self):
        return u"{} - {} - {}".format(self.low, self.mid, self.up)


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
    question = models.ForeignKey('Question', related_name='answers', blank=False, null=True, on_delete=models.SET_NULL)
    choice = models.ForeignKey('Choice', blank=True, null=True, on_delete=models.SET_NULL)
    text = models.TextField(blank=True, null=True)
    value = models.IntegerField(blank=True, null=True)

    @classmethod
    def create(klass, survey_inst, question, choice_id, choice_input=None):
        """Creates Answer parsing input and deciding which fields to set, depending on question type"""
        if question.type in [Question.Type.SINGLE_CHOICE, Question.Type.MULTIPLE_CHOICE]:
            choice = get_object_or_404(Choice, pk=choice_id)
            return klass(survey_instance=survey_inst, question=question, choice=choice,
                         text=choice.language('en').label)
        if question.type in [Question.Type.SINGLE_CHOICE_WITH_FREE_FORM, Question.Type.MULTIPLE_CHOICE_WITH_FREE_FORM]:
            if choice_input:
                return klass(survey_instance=survey_inst, question=question,
                             text=choice_input)
            else:
                choice = get_object_or_404(Choice, pk=choice_id)
                return klass(survey_instance=survey_inst, question=question, choice=choice,
                             text=choice.language('en').label)
        if question.type == Question.Type.SCALE:
            return klass(survey_instance=survey_inst, question=question, text=int(choice_input))
        if question.type == Question.Type.FREE_FORM:
            return klass(survey_instance=survey_inst, question=question, text=choice_input)
