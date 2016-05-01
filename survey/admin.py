from django.contrib import admin
from parler.admin import TranslatableAdmin, TranslatableTabularInline
from survey.models import *


class QuestionGroupInline(TranslatableTabularInline):
    model = QuestionGroup


class QuestionInline(TranslatableTabularInline):
    model = Question


@admin.register(Survey)
class SurveyAdmin(TranslatableAdmin):
    model = Survey


@admin.register(QuestionGroup)
class QuestionGroupAdmin(TranslatableAdmin):
    model = QuestionGroup


@admin.register(Question)
class QuestionAdmin(TranslatableAdmin):
    list_display = ('name', 'type')
    model = Question


@admin.register(ScaleTemplate)
class ScaleTemplateAdmin(TranslatableAdmin):
    model = ScaleTemplate


@admin.register(Choice)
class ChoiceAdmin(TranslatableAdmin):
    model = Choice
    raw_id_fields = ('question',)


@admin.register(SurveyInstance)
class SurveyInstanceAdmin(admin.ModelAdmin):
    model = SurveyInstance
    raw_id_fields = ('courses',)
    readonly_fields = ('url_text', 'url_checksum')


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    model = Answer
    raw_id_fields = ('question', 'survey_instance')
