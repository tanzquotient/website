from django.contrib import messages, admin
from django.db import transaction
from django.contrib.messages import WARNING

from email_system.services import send_group_email, copy_group_email


@admin.action(description="Copy selected emails")
def copy_emails_admin_action(modeladmin, request, queryset):
    for email in queryset:
        copy_group_email(email)
