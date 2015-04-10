from django.shortcuts import render

from django.contrib import messages
from django.contrib.auth.decorators import login_required

from events.models import Event

import django.contrib.auth as auth

import logging
import datetime
log = logging.getLogger('courses')

# Create your views here.

@login_required
def newsletter_list(request, newsletter=True):
    template_name = "export/newsletter.html"
    context={}
        
    context.update({
            'users': auth.models.User.objects.filter(profile__newsletter=newsletter).all()
        })
    return render(request, template_name, context)

@login_required
def no_newsletter_list(request):
    return newsletter_list(request, False)