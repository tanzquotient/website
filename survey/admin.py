from django.db.models import Count, Q, TextField
from django.forms import Textarea
from django.urls import reverse
from django.utils.safestring import mark_safe
from parler.admin import (
    TranslatableAdmin,
    TranslatableStackedInline,
    TranslatableTabularInline,
)
from reversion.admin import VersionAdmin

from courses.filters import SubscribeCourseListFilter, SubscribeOfferingListFilter
from survey.models import *

from .admin_actions import *


class QuestionGroupInline(TranslatableStackedInline):
    model = QuestionGroup
    extra = 0
    readonly_fields = ["questions"]
    fields = ["name", "title", "intro_text", "position", "questions"]
    formfield_overrides = {
        TextField: {
            "widget": Textarea({"rows": "2", "style": "width: 100% !important;"})
        },
    }

    @staticmethod
    def questions(instance) -> str:
        url = reverse("admin:survey_questiongroup_change", args=[instance.pk])
        return (
            mark_safe(
                f"""
        <div><strong><a href="{url}" target="_blank">&#x1F589; Edit Questions</a></strong></div>
        <div><strong>Currently:</strong> {", ".join([q.text for q in instance.question_set.all()]) or "---"}</div>
        """
            )
            if instance.pk
            else "Please save survey before editing questions"
        )


class QuestionInline(TranslatableStackedInline):
    model = Question
    extra = 0
    readonly_fields = ["choices"]
    fields = [
        "name",
        "type",
        "text",
        "note",
        "position",
        "choices",
        "scale",
        "public_review",
        "display",
    ]
    formfield_overrides = {
        TextField: {
            "widget": Textarea({"rows": "2", "style": "width: 100% !important;"})
        },
    }

    @staticmethod
    def choices(instance) -> str:
        url = reverse("admin:survey_question_change", args=[instance.pk])
        return mark_safe(
            f"""
        <div><strong><a href="{url}" target="_blank">&#x1F589; Edit Choices</a></strong></div>
        <div><strong>Currently:</strong> {", ".join([c.value for c in instance.choice_set.all()]) or "---"}</div>
        <div class="help">Only need for single/multiple choice questions</div>
        """
            if instance.pk
            else """
        Please save before editing choices.
        <div class="help">Only need for single/multiple choice questions</div>
        """
        )


class ChoiceInline(TranslatableTabularInline):
    model = Choice
    fields = ["value", "label", "position"]
    extra = 3


@admin.register(Survey)
class SurveyAdmin(TranslatableAdmin):
    model = Survey
    list_display = ["name", "question_groups", "questions", "answers"]
    actions = [export_surveys_xlsx, copy_survey]
    inlines = [QuestionGroupInline]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(
                num_question_groups=Count("questiongroup", distinct=True),
                num_questions=Count("questiongroup__question", distinct=True),
                num_answers=Count(
                    "survey_instances",
                    filter=Q(survey_instances__is_completed=True),
                    distinct=True,
                ),
            )
        )

    @staticmethod
    def questions(instance: Survey) -> str:
        return f"{instance.num_questions} questions in total"

    @staticmethod
    def question_groups(instance: Survey) -> str:
        return f"{instance.num_question_groups} question group(s)"

    @staticmethod
    def answers(instance: Survey) -> str:
        return f"received {instance.num_answers} answers"


@admin.register(Question)
class QuestionAdmin(TranslatableAdmin):
    list_display = ("id", "name", "type")
    model = Question
    inlines = (ChoiceInline,)
    fieldsets = [
        (
            "Question Group Details",
            {
                "fields": [
                    "name",
                    "question_group",
                    "type",
                    "scale",
                    "display",
                    "position",
                    "text",
                    "note",
                ],
                "classes": ["collapse"],
            },
        )
    ]
    list_filter = ("question_group__survey",)


@admin.register(QuestionGroup)
class QuestionGroupAdmin(TranslatableAdmin):
    model = QuestionGroup
    fieldsets = [
        (
            "Question Group Details",
            {
                "fields": ["name", "survey", "position", "title", "intro_text"],
                "classes": ["collapse"],
            },
        )
    ]
    inlines = (QuestionInline,)


@admin.register(Scale)
class ScaleAdmin(TranslatableAdmin):
    model = Scale

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("translations")


@admin.register(SurveyInstance)
class SurveyInstanceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "survey",
        "user",
        "course",
        "date",
        "url_expire_date",
        "last_update",
        "get_url",
    )
    model = SurveyInstance
    raw_id_fields = ("course",)
    show_full_result_count = False
    list_filter = (
        SubscribeOfferingListFilter,
        SubscribeCourseListFilter,
        "url_expire_date",
        "last_update",
    )

    actions = [let_url_expire_now, fix_unintentional_reviews]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("survey", "user", "course__offering")
        )

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False


@admin.register(Answer)
class AnswerAdmin(VersionAdmin):
    list_display = ("id", "survey_instance", "question", "value")
    model = Answer
    raw_id_fields = ("question", "survey_instance")
    show_full_result_count = False

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "survey_instance__survey",
                "survey_instance__user",
                "survey_instance__course__offering",
                "question",
            )
        )

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False
