from django.shortcuts import render, get_object_or_404

from events.models import Event


def event_detail(request, event_id):
    template_name = "events/event_detail.html"
    event = get_object_or_404(Event, pk=event_id)
    context = {
        'event': event,
    }
    return render(request, template_name, context)


def event_reserve(request, event_id):
    template_name = "events/event_reservation.html"
    event = get_object_or_404(Event, pk=event_id)
    context = {
        'event': event,
    }
    return render(request, template_name, context)
