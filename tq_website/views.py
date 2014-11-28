from django.shortcuts import render

from django.contrib import messages
from django.contrib.auth.decorators import login_required

from events.models import Event

import logging
log = logging.getLogger('courses')

# Create your views here.

def home(request):
    template_name = "home.html"
    context={}
    
    events = Event.objects.all()
    if len(events) > 0:
        event = events[0]
    else:
        event = None
    
    context.update({
            'menu': "home",
            'event': event,
        })
    return render(request, template_name, context)

def gallery(request):
    template_name = "gallery.html"
    context={}
        
    context.update({
            'menu': "gallery",
        })
    return render(request, template_name, context)

def faq(request):
    template_name = "faq.html"
    context={}
        
    context.update({
            'menu': "faq",
        })
    return render(request, template_name, context)