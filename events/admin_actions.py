import datetime

from events import services
from events.models import Event


def copy_event(modeladmin, request, queryset) -> None:
    for event in queryset:
        old_event = Event.objects.get(id=event.id)
        new_event = Event.objects.get(id=event.id)
        new_event.pk = None
        new_event.id = None
        new_event._state.adding = True

        new_event.date = old_event.date + datetime.timedelta(days=7)
        if old_event.date_to:
            new_event.date_to = old_event.date_to + datetime.timedelta(days=7)
        new_event.save()

        for lang in ("de", "en"):
            old_event.set_current_language(lang)
            new_event.set_current_language(lang)
            new_event.name = old_event.name
            new_event.description = old_event.description

        new_event.save()


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
