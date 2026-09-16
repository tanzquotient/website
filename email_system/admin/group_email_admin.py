from django.contrib import admin
from django.db.models import Count, Min, Q, QuerySet
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
        "dispatched_at",
        "status",
    ]
    list_filter = ["target_group"]
    search_fields = ["target_group__name"]
    actions = [copy_emails_admin_action]
    fields = [
        "target_group",
        "reply_to",
        "schedule_send",
        "include_unsubscribe",
        "subject",
        "message",
    ]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            super()
            .get_queryset(request)
            .select_related("target_group")
            .prefetch_related("translations")
            .annotate(
                generated_count=Count("generated_emails", distinct=True),
                sent_count=Count(
                    "generated_emails",
                    filter=Q(generated_emails__email__status=EmailStatus.sent),
                    distinct=True,
                ),
                first_generated_at=Min("generated_emails__email__created"),
            )
        )

    def has_change_permission(self, request, obj: GroupEmail | None = None):
        if obj is not None:
            return not obj.is_dispatched()
        return True

    def dispatched_at(self, group_email: GroupEmail) -> str | None:
        if not group_email.generated_count:
            return None
        return timezone.localtime(group_email.first_generated_at).strftime(
            "%d %b %Y %H:%M:%S"
        )

    def status(self, group_email: GroupEmail) -> str | None:
        if not group_email.generated_count:
            return None
        return f"{group_email.sent_count}/{group_email.generated_count} sent"
