from typing import Optional

from django.contrib import admin
from django.contrib.admin.filters import SimpleListFilter
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
from groups.admin.tq_user_admin import UserFullNameAdminMixin


class EventListFilter(SimpleListFilter):
    title = "Event"
    parameter_name = "event"

    def lookups(self, request, model_admin):
        return [
            (event.id, str(event))
            for event in Event.objects.prefetch_related("translations").order_by(
                "-date", "-time_from"
            )
        ]

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        return queryset.filter(event_id=self.value())


class RegistrationScheduleInline(admin.TabularInline):
    model = EventRegistrationSchedule
    extra = 0
    fields = ("action", "run_at", "executed")
    readonly_fields = ("executed",)
    verbose_name = "Schedule opening or closing registration"
    show_change_link = False


@admin.register(Event)
class EventAdmin(UserFullNameAdminMixin, TranslatableAdmin):
    list_display = (
        "name",
        "get_responsible",
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

    autocomplete_fields = ["responsible"]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("room")
            .prefetch_related("translations", "responsible")
        )

    @staticmethod
    @admin.display(description="Responsible")
    def get_responsible(event: Event) -> Optional[str]:
        responsible = event.responsible.all()
        if not responsible:
            return None
        return ", ".join([r.get_full_name() for r in responsible])

    @staticmethod
    @admin.display(description="View")
    def view_button(event: Event) -> str:
        if event is None or event.pk is None:
            return "—"
        label = "Preview" if not event.published else "View"
        return mark_safe(
            '<a class="button" '
            'style="text-decoration: none; text-transform: uppercase;" '
            f'href="{event.detail_url()}" target="_blank">{label}</a>'
        )


@admin.register(EventCategory)
class EventCategoryAdmin(TranslatableAdmin):
    list_display = ("name", "position", "description")
    fields = ("name", "position", "teaser", "description", "is_featured", "image")
    model = EventCategory

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("translations")


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ["id", "event", "user", "timestamp"]
    list_filter = [EventListFilter]
    model = EventRegistration
    show_full_result_count = False

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("event", "user")
            .prefetch_related("event__translations")
        )
