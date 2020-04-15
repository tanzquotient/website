from django.contrib import messages
from django.contrib.messages import WARNING

from email_system.services import send_email, copy_email


def send_emails_admin_action(modeladmin, request, queryset):
    for email in queryset:
        if email.is_sent():
            messages.add_message(request, WARNING, 'Skipping "{}". This email has already been sent'.format(email))
        else:
            send_email(email)

send_emails_admin_action.short_description = "Send selected emails"


def copy_emails_admin_action(modeladmin, request, queryset):
    for email in queryset:
        copy_email(email)

copy_emails_admin_action.short_description = "Copy selected emails"