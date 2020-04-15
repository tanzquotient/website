from django.contrib import admin
from django.contrib.admin import ModelAdmin

from email_system.models import GeneratedIndividualEmail


@admin.register(GeneratedIndividualEmail)
class GeneratedIndividualEmailAdmin(ModelAdmin):
    model = GeneratedIndividualEmail

    list_display = ['subject', 'to', 'source']
    list_filter = []
    search_fields = ['email__to', 'email__subject']
    actions = []

    def subject(self, obj):
        return obj.email.subject

    def to(self, obj):
        return obj.email.to


    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
