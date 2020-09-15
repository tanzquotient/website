from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404, redirect

from events.models import Event
from events.models.event_registration import EventRegistration


def detail(request, event_id):
    template_name = "events/event_detail.html"
    event = get_object_or_404(Event, pk=event_id)
    context = {
        'event': event,
        'user_registered': event.is_registered(request.user)
    }
    return render(request, template_name, context)


@login_required
def register(request, event_id):
    user_id = request.user.id
    try:
        registration = EventRegistration(user_id=user_id, event_id=event_id)
        registration.save()
    except IntegrityError:
        pass  # Already registered
    return redirect('events:registration_confirmation', event_id)


def registration_confirmation(request, event_id):
    template_name = "events/event_detail.html"
    event = get_object_or_404(Event, pk=event_id)
    context = {
        'event': event,
        'user_registered': event.is_registered(request.user),
        'is_registration_confirmation': True,
    }
    return render(request, template_name, context)
