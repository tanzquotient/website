from django.contrib import admin
from parler.admin import TranslatableAdmin, TranslatableTabularInline

import courses
from .admin_actions import *
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

    actions = [export_surveys_xlsx, copy_survey]


@admin.register(QuestionGroup)
class QuestionGroupAdmin(TranslatableAdmin):
    list_display = ('name', 'survey')
    model = QuestionGroup
    inlines = (QuestionInline,)
    list_filter = ('survey', )


@admin.register(Question)
class QuestionAdmin(TranslatableAdmin):
    list_display = ('id', 'name', 'type')
    model = Question
    inlines = (ChoiceInline,)
    list_filter = ('question_group__survey', )


@admin.register(ScaleTemplate)
class ScaleTemplateAdmin(TranslatableAdmin):
    model = ScaleTemplate


@admin.register(Choice)
class ChoiceAdmin(TranslatableAdmin):
    list_display = ('get_question_name', 'label', 'position')
    model = Choice
    raw_id_fields = ('question',)
    list_filter = ('question__question_group__survey',)


@admin.register(SurveyInstance)
class SurveyInstanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'invitation_sent', 'survey', 'user', 'course', 'date', 'url_expire_date','last_update','get_url')
    model = SurveyInstance
    raw_id_fields = ('course',)
    list_filter = (courses.filters.SubscribeOfferingListFilter, courses.filters.SubscribeCourseListFilter, 'url_expire_date', 'last_update','invitation_sent')

    actions = [send_invitations,let_url_expire_now]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id','survey_instance', 'question', 'choice', 'text')
    model = Answer
    raw_id_fields = ('question', 'survey_instance')
