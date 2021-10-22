from django.contrib import admin
from parler.admin import TranslatableAdmin

from events.admin_actions import *
from events.filters.event_date_filter import EventDateFilter
from events.models import Event, EventCategory, EventRegistration


@admin.register(Event)
class EventAdmin(TranslatableAdmin):
    list_display = ('name', 'date', 'format_time', 'room', 'special', 'display')
    list_filter = (EventDateFilter, 'room',)

    model = Event

    actions = [copy_event, export_registrations_csv, export_registrations_excel]

    fieldsets = [
        ('What?', {
            'fields': ['name', 'category', 'registration_enabled', 'max_participants', 'description', 'image']}),
        ('When?', {
            'fields': ['date', 'time_from', 'time_to', 'cancelled']}),
        ('Where?', {
            'fields': ['room', ]}),
        ('Billing', {
            'fields': ['price_with_legi', 'price_without_legi', 'price_special', ]}),
        ('Admin', {
            'fields': ['special', 'display'],}),
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
