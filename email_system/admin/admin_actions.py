from django.contrib import admin, messages
from django.contrib.messages import WARNING

from email_system.services import copy_group_email
from email_system.models.choices import GroupEmailState


@admin.action(description="Send selected emails")
def send_emails_admin_action(modeladmin, request, queryset):
    for email in queryset:
        if email.state != GroupEmailState.DRAFT:
            messages.add_message(
                request,
                WARNING,
                f"Skipping {email}. You can only send emails in a draft state.",
            )
        else:
            email.state = GroupEmailState.QUEUED
            email.save()


def copy_emails_admin_action(modeladmin, request, queryset):
    for email in queryset:
        copy_group_email(email)


copy_emails_admin_action.short_description = "Copy selected emails"
