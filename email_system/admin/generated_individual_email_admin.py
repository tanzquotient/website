from typing import Any
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.http.request import HttpRequest
from django.utils import timezone

from post_office.models import Email

from email_system.models import GeneratedIndividualEmail


@admin.register(GeneratedIndividualEmail)
class GeneratedIndividualEmailAdmin(ModelAdmin):
    model = GeneratedIndividualEmail

    list_display = ["subject", "to", "source", "status", "last_updated"]
    list_filter = ["email__status"]
    search_fields = ["email__to", "email__subject"]
    actions = []

    def subject(self, obj):
        return obj.email.subject

    def to(self, obj):
        return obj.email.to

    def has_add_permission(self, request: HttpRequest):
        return False

    def has_change_permission(self, request: HttpRequest, obj: Any | None = None):
        return False

    def has_delete_permission(
        self, request: HttpRequest, obj: Any | None = None
    ) -> bool:
        return False

    def status(self, generated_individual_email: GeneratedIndividualEmail) -> str:
        return Email.STATUS_CHOICES[generated_individual_email.email.status][1]

    def last_updated(self, generated_individual_email: GeneratedIndividualEmail) -> str:
        return timezone.localtime(
            generated_individual_email.email.last_updated
        ).strftime("%d %b %Y %H:%M:%S")
