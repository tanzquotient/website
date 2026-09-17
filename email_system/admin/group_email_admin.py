from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils import timezone
from parler.admin import TranslatableAdmin
from post_office.models import STATUS as EmailStatus

from email_system.admin.admin_actions import (
    copy_emails_admin_action,
)
from email_system.models import GroupEmail


@admin.register(GroupEmail)
class GroupEmailAdmin(TranslatableAdmin):
    model = GroupEmail

    list_display = [
        "subject",
        "target_group",
        "schedule_send",
    ]
    list_filter = ["target_group"]
    search_fields = ["target_group__name"]
    actions = [copy_emails_admin_action]
    fields = [
        "target_group",
        "reply_to",
        "schedule_send",
        "dispatched_at",
        "status",
        "include_unsubscribe",
        "subject",
        "message",
    ]
    readonly_fields = ["dispatched_at", "status"]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            super()
            .get_queryset(request)
            .select_related("target_group")
            .prefetch_related("translations")
        )

    def has_change_permission(self, request, obj: GroupEmail | None = None):
        if obj is not None:
            return not obj.is_dispatched()
        return True

    def dispatched_at(self, group_email: GroupEmail) -> str | None:
        if not group_email.is_dispatched():
            return None
        return timezone.localtime(
            group_email.generated_emails.first().email.created
        ).strftime("%d %b %Y %H:%M:%S")

    def status(self, group_email: GroupEmail) -> str | None:
        if not group_email.is_dispatched():
            return None
        generated_emails = group_email.generated_emails
        return f"{generated_emails.filter(email__status=EmailStatus.sent).count()}/{generated_emails.count()} sent"
