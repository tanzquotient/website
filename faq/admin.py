from django.contrib import admin
from parler.admin import TranslatableAdmin, TranslatableTabularInline

from faq.models import *


class QuestionInline(TranslatableTabularInline, admin.TabularInline):
    model = Question
    extra = 0


@admin.register(QuestionGroup)
class QuestionGroupAdmin(admin.ModelAdmin):
    list_display = ("name",)
    inlines = (QuestionInline,)


@admin.register(Question)
class QuestionAdmin(TranslatableAdmin):
    list_display = ("question_text", "display", "question_group")
    search_fields = ["translations__question_text", "translations__answer_text"]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("question_group")
            .prefetch_related("translations")
        )
