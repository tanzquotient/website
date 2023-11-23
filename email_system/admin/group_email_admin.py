from django.contrib import admin
from parler.admin import TranslatableAdmin

from email_system.admin.admin_actions import (
    send_emails_admin_action,
    copy_emails_admin_action,
)
from email_system.models import GroupEmail


@admin.register(GroupEmail)
class GroupEmailAdmin(TranslatableAdmin):
    model = GroupEmail

    list_display = ["subject", "target_group", "sent_at"]
    list_filter = ["target_group"]
    search_fields = ["target_group__name"]
    actions = [send_emails_admin_action, copy_emails_admin_action]
    fields = ["target_group", "reply_to", "subject", "message"]

    def has_change_permission(self, request, obj=None):
        if obj is not None:
            return not obj.is_sent()
        return True
