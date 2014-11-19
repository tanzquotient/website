from django.contrib import admin

from faq.models import *

class QuestionInline(admin.TabularInline):
    model=Question
    fields = ('question_text','answer_text','display',"position",)
    # define the sortable
    sortable_field_name = "position"
    extra=0
    
class QuestionGroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = (QuestionInline,)
    
# Register your models here.
admin.site.register(QuestionGroup, QuestionGroupAdmin)