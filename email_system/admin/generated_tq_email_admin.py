from django.contrib import admin
from parler.admin import TranslatableAdmin

from email_system.models import GeneratedTQEmail


@admin.register(GeneratedTQEmail)
class GeneratedTQEmailAdmin(TranslatableAdmin):
    model = GeneratedTQEmail

    list_display = ['source', 'email']
    list_filter = []
    search_fields = ['source__subject']
    actions = []

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
