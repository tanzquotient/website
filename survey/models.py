from django.core.urlresolvers import reverse
from django.db import models
from parler.models import TranslatableModel, TranslatedFields
from django.conf import settings
from . import services
from django.shortcuts import get_object_or_404


class Survey(TranslatableModel):
    name = models.CharField(max_length=255, blank=False)

    translations = TranslatedFields(
        intro_text=models.TextField(blank=True, null=True),
    )

    def get_test_url(self):
        return reverse("survey:survey_test", kwargs={'survey_id': self.id})

    get_test_url.short_description ="Test url"

    def __str__(self):
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

    def __str__(self):
        return self.name


class Question(TranslatableModel):
    class Type:
        SINGLE_CHOICE = 'c'
        SINGLE_CHOICE_WITH_FREE_FORM = 'cf'
        MULTIPLE_CHOICE = 'm'
        MULTIPLE_CHOICE_WITH_FREE_FORM = 'mf'
        SCALE = 's'
        FREE_FORM = 'f'

        CHOICES = ((SINGLE_CHOICE,'single choice'),
                   (SINGLE_CHOICE_WITH_FREE_FORM,'single choice with free form'),
                   (MULTIPLE_CHOICE,'multiple choice'),
                   (MULTIPLE_CHOICE_WITH_FREE_FORM,'multiple choice with free form'),
                   (SCALE,'scale'),
                   (FREE_FORM,'free form'))

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

    def scale_label(self, which):
        if self.type != Question.Type.SCALE:
            return None
        if self.scale_template == None:
            return str(which)

        if which == 1:
            return self.scale_template.low
        elif which == 2:
            return "-"
        elif which == 3:
            return self.scale_template.mid or "-"
        elif which == 4:
            return "-"
        elif which == 5:
            return self.scale_template.up
        else:
            return None

    def scale_label1(self):
        return self.scale_label(1)

    def scale_label2(self):
        return self.scale_label(2)

    def scale_label3(self):
        return self.scale_label(3)

    def scale_label4(self):
        return self.scale_label(4)

    def scale_label5(self):
        return self.scale_label(5)

    class Meta:
        ordering = ['position']

    def __str__(self):
        return self.name


class ScaleTemplate(TranslatableModel):
    translations = TranslatedFields(
        low=models.CharField(max_length=30),
        mid=models.CharField(max_length=30, blank=True, null=True),
        up=models.CharField(max_length=30)
    )

    def __str__(self):
        return"{} - {} - {}".format(self.low, self.mid, self.up)


class Choice(TranslatableModel):
    question = models.ForeignKey('Question', blank=False, null=True, on_delete=models.CASCADE)
    position = models.PositiveSmallIntegerField("Position", default=0)

    translations = TranslatedFields(
        label=models.CharField(max_length=255)
    )

    def get_question_name(self):
        return self.question.name

    get_question_name.short_description = "Question Name"

    class Meta:
        ordering = ['position']


class SurveyInstance(models.Model):
    survey = models.ForeignKey('Survey', related_name='survey_instances', blank=False,
                               null=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='survey_instances', blank=False,
                             null=False)
    course = models.ForeignKey('courses.Course', related_name='survey_instances', blank=True, null=True)
    date = models.DateTimeField(blank=False, null=False, auto_now_add=True)
    last_update = models.DateTimeField(blank=True, null=True, auto_now_add=False)
    url_expire_date = models.DateTimeField(blank=True, null=True, auto_now_add=False)
    invitation_sent = models.BooleanField(blank=False, null=False, default=False)

    def get_url(self):
        return services.create_url(self)

    def __str__(self):
        if self.course:
            return"{} for {} of {}".format(self.survey, self.course, self.user)
        else:
            return"{} of {}".format(self.survey, self.user)


class Answer(models.Model):
    survey_instance = models.ForeignKey('SurveyInstance', related_name='answers', blank=False, null=True,
                                        on_delete=models.CASCADE)
    question = models.ForeignKey('Question', related_name='answers', blank=False, null=True, on_delete=models.SET_NULL)
    choice = models.ForeignKey('Choice', blank=True, null=True, on_delete=models.SET_NULL)
    text = models.TextField(blank=True, null=True)

    @classmethod
    def create(klass, survey_inst, question, choice, choice_input=None):
        """Creates Answer parsing input and deciding which fields to set, depending on question type"""
        if question.type in [Question.Type.SINGLE_CHOICE, Question.Type.MULTIPLE_CHOICE]:
            # here we expect choice to be a valid id
            choice = get_object_or_404(Choice, pk=choice)
            choice.set_current_language('en')
            return klass(survey_instance=survey_inst, question=question, choice=choice,
                         text=choice.label)
        if question.type in [Question.Type.SINGLE_CHOICE_WITH_FREE_FORM, Question.Type.MULTIPLE_CHOICE_WITH_FREE_FORM]:
            if choice == 'freeform':
                return klass(survey_instance=survey_inst, question=question,
                                 text=choice_input)
            else:
                choice = get_object_or_404(Choice, pk=choice)
                choice.set_current_language('en')
                return klass(survey_instance=survey_inst, question=question, choice=choice,
                             text=choice.label)
        if question.type == Question.Type.SCALE:
            return klass(survey_instance=survey_inst, question=question, text=choice_input)
        if question.type == Question.Type.FREE_FORM:
            if choice == 'default':
                return klass(survey_instance=survey_inst, question=question, text=choice_input)
            else:
                choice = get_object_or_404(Choice, pk=choice)
                return klass(survey_instance=survey_inst, question=question, choice=choice, text=choice_input)

    def __str__(self):
        return"q({})-c({}): {}".format(self.question, self.choice, self.text)
