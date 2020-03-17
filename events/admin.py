from django.contrib import admin
from daterange_filter.filter import DateRangeFilter
from parler.admin import TranslatableAdmin

from events.admin_actions import *
from events.filters.event_date_filter import EventDateFilter
from events.models import Organise, Event


class OrganisatorInline(admin.TabularInline):
    model = Organise
    extra = 1
    fk_name = 'event'

    raw_id_fields = ('organiser',)


@admin.register(Event)
class EventAdmin(TranslatableAdmin):
    list_display = ('name', 'date', 'format_time', 'room', 'format_prices', 'format_organisators', 'special', 'display')
    list_filter = (EventDateFilter, ('date', DateRangeFilter), 'room',)
    inlines = (OrganisatorInline,)

    model = Event

    actions = [copy_event, ]

    fieldsets = [
        ('What?', {
            'fields': ['name', 'description', 'image']}),
        ('When?', {
            'fields': ['date', 'time_from', 'time_to', 'cancelled']}),
        ('Where?', {
            'fields': ['room', ]}),
        ('Billing', {
            'fields': ['price_with_legi', 'price_without_legi', 'price_special', ]}),
        ('Admin', {
            'fields': ['special', 'display'],}),
    ]
