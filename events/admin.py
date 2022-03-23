from django.contrib import admin
from parler.admin import TranslatableAdmin

from events.admin_actions import *
from events.filters.event_date_filter import EventDateFilter
from events.models import Event, EventCategory, EventRegistration


@admin.register(Event)
class EventAdmin(TranslatableAdmin):
    list_display = ('name', 'date', 'special', 'display', 'time_from', 'date_to', 'time_to', 'room')
    list_filter = (EventDateFilter, 'room',)

    model = Event

    actions = [copy_event, export_registrations_csv, export_registrations_excel]

    fieldsets = [
        ('Info', {'fields': ['name', 'category', 'description', 'image']}),
        ('Options', {'fields': ['special', 'display', 'cancelled', 'registration_enabled', 'max_participants']}),
        ('Date & Time', {'fields': ['date', 'time_from', 'date_to', 'time_to']}),
        ('Location', {'fields': ['room']}),
        ('Price schema', {'fields': ['price_with_legi', 'price_without_legi', 'price_special']}),
    ]


@admin.register(EventCategory)
class EventCategoryAdmin(TranslatableAdmin):
    list_display = ('name', 'description')
    fields = ('name', 'teaser', 'description', 'is_featured', 'image')
    model = EventCategory


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['id', 'event', 'user', 'timestamp']
    list_filter = ['event']
    model = EventRegistration
