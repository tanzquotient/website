#!/usr/bin/python
# -*- coding: UTF-8 -*-
from django.contrib import admin
from parler.admin import TranslatableAdmin, TranslatableTabularInline

from admin_actions import send_invitations
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
    list_display = ('id', 'invitation_sent', 'survey', 'user', 'course', 'date', 'last_update')
    model = SurveyInstance
    raw_id_fields = ('course',)
    readonly_fields = ('url_text', 'url_checksum')

    actions = [send_invitations,]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    model = Answer
    raw_id_fields = ('question', 'survey_instance')
