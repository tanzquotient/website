from django.shortcuts import render

from django.contrib import messages
from django.contrib.auth.decorators import login_required

import logging
log = logging.getLogger('courses')

# Create your views here.

def home(request):
    template_name = "home.html"
    context={}
        
    context.update({
            'menu': "home",
        })
    return render(request, template_name, context)

def events(request):
    template_name = "events.html"
    context={}
        
    context.update({
            'menu': "events",
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