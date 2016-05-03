from django.contrib import admin
from parler.admin import TranslatableAdmin, TranslatableTabularInline
from survey.models import *


class QuestionGroupInline(TranslatableTabularInline):
    model = QuestionGroup
    exclude = ('intro_text', )


class QuestionInline(TranslatableTabularInline):
    model = Question
    exclude = ('text', 'note')

class ChoiceInline(TranslatableTabularInline):
    model = Choice


@admin.register(Survey)
class SurveyAdmin(TranslatableAdmin):
    list_display = ('name', 'get_test_url')
    model = Survey
    inlines = (QuestionGroupInline,)


@admin.register(QuestionGroup)
class QuestionGroupAdmin(TranslatableAdmin):
    model = QuestionGroup
    inlines = (QuestionInline,)


@admin.register(Question)
class QuestionAdmin(TranslatableAdmin):
    list_display = ('name', 'type')
    model = Question
    inlines = (ChoiceInline,)


@admin.register(ScaleTemplate)
class ScaleTemplateAdmin(TranslatableAdmin):
    model = ScaleTemplate


@admin.register(Choice)
class ChoiceAdmin(TranslatableAdmin):
    list_display = ('get_question_name', 'label', 'position')
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
