from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.shortcuts import render

from django.contrib import messages
from django.contrib.auth.decorators import login_required

from events.models import Event

import django.contrib.auth as auth

import logging
import datetime

log = logging.getLogger('tq')


# Create your views here.

@staff_member_required
def newsletter_list(request, newsletter=True):
    template_name = "export/user_emails.html"
    context = {}

    context.update({
        'users': User.objects.filter(is_active=1, profile__newsletter=newsletter).all()
    })
    return render(request, template_name, context)


@staff_member_required
def no_newsletter_list(request):
    return newsletter_list(request, False)


@staff_member_required
def get_involved_list(request, get_involved=True):
    template_name = "export/user_emails.html"
    context = {}

    context.update({
        'users': User.objects.filter(is_active=1, profile__get_involved=get_involved).all()
    })
    return render(request, template_name, context)


@staff_member_required
def not_get_involved_list(request):
    return get_involved_list(request, False)
