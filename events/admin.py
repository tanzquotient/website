from django.contrib import admin
from parler.admin import TranslatableAdmin

from events.admin_actions import *
from events.filters.event_date_filter import EventDateFilter
from events.models import Event, EventCategory


@admin.register(Event)
class EventAdmin(TranslatableAdmin):
    list_display = ('name', 'date', 'format_time', 'room', 'special', 'display')
    list_filter = (EventDateFilter, 'room',)

    model = Event

    actions = [copy_event, ]

    fieldsets = [
        ('What?', {
            'fields': ['name', 'category', 'reservation_enabled', 'max_participants', 'description', 'image']}),
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
    model = EventCategory
