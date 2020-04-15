from django.contrib import admin
from parler.admin import TranslatableAdmin

from email_system.models import TQEmail


@admin.register(TQEmail)
class TQEmailAdmin(TranslatableAdmin):
    model = TQEmail

    list_display = ['subject', 'target_group', 'sent_at']
    list_filter = ['target_group']
    search_fields = ['subject', 'target_group__name']
    actions = []

    def has_change_permission(self, request, obj=None):
        if obj is not None:
            return not obj.is_sent()
        return True

