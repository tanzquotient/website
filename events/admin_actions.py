import datetime

from events.models import Event


def copy_event(modeladmin, request, queryset):
    for event in queryset:
        old_id = event.id
        event.date = event.date + datetime.timedelta(days=7)
        event.id = None
        event.save()
        old_event = Event.objects.get(id=old_id)

        event.set_current_language('de')
        old_event.set_current_language('de')
        event.name = old_event.name
        event.description = old_event.description

        event.set_current_language('en')
        old_event.set_current_language('en')
        event.name = old_event.name
        event.description = old_event.description

        event.save()


copy_event.short_description = "Create copy of selected events (adding one week)"
