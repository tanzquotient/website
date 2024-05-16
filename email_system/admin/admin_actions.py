from django.contrib import messages, admin
from django.db import transaction
from django.contrib.messages import WARNING

from email_system.services import send_group_email, copy_group_email


@admin.action(description="Send selected emails")
def send_emails_admin_action(modeladmin, request, queryset):
    for email in queryset:
        if email.is_sent():
            messages.add_message(
                request,
                WARNING,
                f"Skipping {email}. This email has already been sent",
            )
        else:
            with transaction.atomic():
                send_group_email(email)


@admin.action(description="Copy selected emails")
def copy_emails_admin_action(modeladmin, request, queryset):
    for email in queryset:
        copy_group_email(email)
