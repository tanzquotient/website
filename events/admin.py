from django.contrib import admin
from django.utils.safestring import mark_safe
from parler.admin import TranslatableAdmin

from events.admin_actions import *
from events.filters.event_date_filter import EventDateFilter
from events.models import (
    Event,
    EventCategory,
    EventRegistration,
    EventRegistrationSchedule,
)


class RegistrationScheduleInline(admin.TabularInline):
    model = EventRegistrationSchedule
    extra = 0
    fields = ("action", "run_at", "executed")
    readonly_fields = ("executed",)
    verbose_name = "Schedule opening or closing registration"
    show_change_link = False


@admin.register(Event)
class EventAdmin(TranslatableAdmin):
    list_display = (
        "name",
        "special",
        "display",
        "published",
        "view_button",
        "date",
        "time_from",
        "date_to",
        "time_to",
        "room",
    )
    list_filter = (
        EventDateFilter,
        "room",
        "category",
        "display",
        "published",
    )

    model = Event

    inlines = [RegistrationScheduleInline]

    actions = [copy_event, export_registrations_csv, export_registrations_excel]

    readonly_fields = ("view_button",)

    fieldsets = [
        ("Info", {"fields": ["name", "category", "description", "image"]}),
        (
            "Options",
            {
                "fields": [
                    "special",
                    "display",
                    "published",
                    "view_button",
                    "cancelled",
                    "registration_enabled",
                    "max_participants",
                    "show_category_description",
                ]
            },
        ),
        ("Date & Time", {"fields": ["date", "time_from", "date_to", "time_to"]}),
        ("Location", {"fields": ["room"]}),
        ("Responsible", {"fields": ["responsible"]}),
        (
            "Price schema",
            {"fields": ["price_with_legi", "price_without_legi", "price_special"]},
        ),
    ]

    filter_horizontal = ["responsible"]

    def view_button(self, obj):
        if obj is None or obj.pk is None:
            return "—"
        label = "Preview" if not obj.published else "View"
        return mark_safe(
            '<a class="button" '
            'style="text-decoration: none; text-transform: uppercase;" '
            f'href="{obj.detail_url()}" target="_blank">{label}</a>'
        )

    view_button.short_description = "View"


@admin.register(EventCategory)
class EventCategoryAdmin(TranslatableAdmin):
    list_display = ("name", "position", "description")
    fields = ("name", "position", "teaser", "description", "is_featured", "image")
    model = EventCategory


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ["id", "event", "user", "timestamp"]
    list_filter = ["event"]
    model = EventRegistration
