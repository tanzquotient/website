from django.contrib import admin
from events.models import *

# Register your models here.

class OrganisatorInline(admin.TabularInline):
    model = Organise
    extra = 1
    fk_name = 'event'
    
    # define the raw_id_fields (grappelli feature)
    raw_id_fields = ('organiser',)
    # define the autocomplete_lookup_fields (grappelli feature)
    autocomplete_lookup_fields = {
        'fk': ['organiser'],
    }
    
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'date','format_time','room','format_prices','format_organisators')
    list_filter = ('date', 'room',)
    inlines = (OrganisatorInline,)
    
    model = Event
    fieldsets = [
        ('What?', {
                     'classes': ("grp-collapse grp-open",),
                     'fields': ['name','description']}),
        ('When?', {
                   'classes': ("grp-collapse grp-open",),
                   'fields': ['date','time_from','time_to',]}),
        ('Where?', {
                    'classes': ("grp-collapse grp-open",),
                    'fields': ['room',]}),
        ('Billing', {
                     'classes': ("grp-collapse grp-open",),
                     'fields': ['price_with_legi','price_without_legi']}),
        ('Etc', {
                 'classes': ("grp-collapse grp-closed",),
                 'fields': ['comment'],}),
    ]
    
admin.site.register(Event,EventAdmin)