from django.db.models import TextField
from django.forms import Textarea
from django.urls import reverse
from django.utils.safestring import mark_safe, SafeString
from parler.admin import TranslatableAdmin, TranslatableTabularInline, TranslatableStackedInline

from courses.filters import SubscribeOfferingListFilter, SubscribeCourseListFilter
from survey.models import *
from .admin_actions import *


class QuestionGroupInline(TranslatableStackedInline):
    model = QuestionGroup
    extra = 0
    readonly_fields = ['questions']
    fields = ['name', 'title', 'intro_text', 'position', 'questions']
    formfield_overrides = {
        TextField: {'widget': Textarea({'rows': '2', 'style': 'width: 100% !important;'})},
    }

    @staticmethod
    def questions(instance) -> str:
        url = reverse(f'admin:survey_questiongroup_change', args=[instance.pk])
        return mark_safe(f'''
        <div><strong><a href="{url}" target="_blank">&#x1F589; Edit Questions</a></strong></div>
        <div><strong>Currently:</strong> {', '.join([q.text for q in instance.question_set.all()])} </div>
        ''') if instance.pk else 'Please save survey before editing questions'


class QuestionInline(TranslatableStackedInline):
    model = Question
    extra = 0
    readonly_fields = ['choices']
    fields = ['name', 'type', 'text', 'note', 'position',  'choices', 'scale']
    formfield_overrides = {
        TextField: {'widget': Textarea({'rows': '2', 'style': 'width: 100% !important;'})},
    }

    @staticmethod
    def choices(instance) -> str:
        url = reverse(f'admin:survey_question_change', args=[instance.pk])
        return mark_safe(f'''
        <div><strong><a href="{url}" target="_blank"><i class="fa-solid fa-pencil"></i>&#x1F589; Edit Choices</a></strong></div>
        <div><strong>Currently:</strong> {", ".join([c.value for c in instance.choice_set.all()]) or "no choices set"}</div>
         <div class="help">Only need for single/multiple choice questions</div>
        '''if instance.pk else '''
        Please save before editing choices.
        <div class="help">Only need for single/multiple choice questions</div>
        ''')

    def get_form(self, request, obj=None, **kwargs):
        help_texts = {'policy_difference': 'Help text explaining policy difference'}
        kwargs.update({'help_texts': help_texts})
        return super(QuestionInline, self).get_form(request, obj, **kwargs)


class ChoiceInline(TranslatableTabularInline):
    model = Choice
    fields = ['value', 'label', 'position']
    extra = 3


@admin.register(Survey)
class SurveyAdmin(TranslatableAdmin):
    model = Survey
    list_display = ['name', 'question_groups', 'questions']
    actions = [export_surveys_xlsx, copy_survey]
    inlines = [QuestionGroupInline]

    @staticmethod
    def questions(instance: Survey) -> str:
        return f"{Question.objects.filter(question_group__survey=instance).count()} questions in total"

    @staticmethod
    def question_groups(instance: Survey) -> str:
        return f"{instance.questiongroup_set.count()} question group(s)"


@admin.register(Question)
class QuestionAdmin(TranslatableAdmin):
    list_display = ('id', 'name', 'type')
    model = Question
    inlines = (ChoiceInline,)
    fieldsets = [('Question Group Details', {
        'fields': ['name', 'question_group', 'type', 'scale', 'display', 'position', 'text', 'note'],
        'classes': ['collapse']
    })]
    list_filter = ('question_group__survey', )


@admin.register(QuestionGroup)
class QuestionGroupAdmin(TranslatableAdmin):
    model = QuestionGroup
    fieldsets = [('Question Group Details', {
        'fields': ['name', 'survey', 'position', 'title', 'intro_text'],
        'classes': ['collapse']
    })]
    inlines = (QuestionInline,)


@admin.register(Scale)
class ScaleAdmin(TranslatableAdmin):
    model = Scale


@admin.register(SurveyInstance)
class SurveyInstanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'invitation_sent', 'survey', 'user', 'course', 'date', 'url_expire_date', 'last_update', 'get_url')
    model = SurveyInstance
    raw_id_fields = ('course',)
    list_filter = (SubscribeOfferingListFilter, SubscribeCourseListFilter, 'url_expire_date', 'last_update', 'invitation_sent')

    actions = [let_url_expire_now]

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'survey_instance', 'question', 'value')
    model = Answer
    raw_id_fields = ('question', 'survey_instance')

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False
