import datetime

from events import services
from events.models import Event


def copy_event(modeladmin, request, queryset) -> None:
    for event in queryset:
        old_id = event.id
        event.date = event.date + datetime.timedelta(days=7)
        if event.date_to:
            event.date_to = event.date_to + datetime.timedelta(days=7)
        event.id = None
        event.save()
        old_event = Event.objects.get(id=old_id)

        event.set_current_language("de")
        old_event.set_current_language("de")
        event.name = old_event.name
        event.description = old_event.description

        event.set_current_language("en")
        old_event.set_current_language("en")
        event.name = old_event.name
        event.description = old_event.description

        event.save()


copy_event.short_description = "Create copy of selected events (adding one week)"


def export_registrations_csv(modeladmin, request, queryset):
    event_ids = []
    for c in queryset:
        event_ids.append(c.id)
    return services.export_registrations(event_ids, "csv")


export_registrations_csv.short_description = "Export registrations (CSV)"


def export_registrations_excel(modeladmin, request, queryset):
    event_ids = []
    for c in queryset:
        event_ids.append(c.id)
    return services.export_registrations(event_ids, "xlsx")


export_registrations_excel.short_description = "Export registrations (Excel)"
