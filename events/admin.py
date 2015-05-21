from django.contrib import admin
from events.models import *

from events.admin_actions import *

# Register your models here.

class OrganisatorInline(admin.TabularInline):
    model = Organise
    extra = 1
    fk_name = 'event'

    raw_id_fields = ('organiser',)


class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'format_time', 'room', 'format_prices', 'format_organisators', 'special', 'display')
    list_filter = ('date', 'room',)
    inlines = (OrganisatorInline,)

    model = Event

    actions = [copy_event, ]

    fieldsets = [
        ('What?', {
            'fields': ['name', 'description', 'image']}),
        ('When?', {
            'fields': ['date', 'time_from', 'time_to', ]}),
        ('Where?', {
            'fields': ['room', ]}),
        ('Billing', {
            'fields': ['price_with_legi', 'price_without_legi', 'price_special', ]}),
        ('Admin', {
            'fields': ['special', 'display'], }),
    ]


admin.site.register(Event, EventAdmin)
