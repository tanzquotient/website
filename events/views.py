from django.shortcuts import render
from events.models import Event

# Create your views here.
def events(request):
    template_name = "events/events.html"
    context={}
        
    context.update({
            'menu': "events",
            'events': Event.objects.all()
        })
    return render(request, template_name, context)