from django.contrib import admin
from parler.admin import TranslatableAdmin, TranslatableTabularInline, TranslatableModelForm
from faq.models import *


class QuestionInline(TranslatableTabularInline, admin.TabularInline):
    model = Question
    extra = 0


@admin.register(QuestionGroup)
class QuestionGroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = (QuestionInline,)


@admin.register(Question)
class QuestionAdmin(TranslatableAdmin):
    search_fields = ['translations__question_text', 'translations__answer_text']
