from django.contrib import admin

from email_system.services import copy_group_email


@admin.action(description="Copy selected emails")
def copy_emails_admin_action(modeladmin, request, queryset):
    for email in queryset:
        copy_group_email(email)
