from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.http import Http404
from django.views.generic import TemplateView, ListView
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _

from django.contrib import messages
from django.contrib.auth.decorators import login_required

from models import *

from forms import *

import services

from django.contrib.auth.models import User

import logging
log = logging.getLogger('courses')

# Create your views here.

def course_list(request):
    template_name = "courses/list.html"
    context={}
    context.update({
        'menu': "courses",
    })
    
    offerings=services.get_offerings_to_display()
    c_offerings=[]
    for offering in offerings:
        weekday_list = []
        course_set=offering.course_set
        for (w,w_name) in WEEKDAYS:
            weekday_dict = {}
            weekday_dict['weekday']=WEEKDAYS_TRANS[w]
            weekday_dict['courses']=course_set.weekday(w)
            if (w=='sat' or w=='sun') and weekday_dict['courses'].__len__() == 0:
                pass
            else:
                weekday_list.append(weekday_dict)
        
        #add courses that have no weekday entry yet
        weekday_dict = {}
        weekday_dict['weekday']=_("Unknown weekday")
        weekday_dict['courses']=course_set.weekday(None)
        if weekday_dict['courses'].__len__() != 0:
            weekday_list.append(weekday_dict)
            
        c_offerings.append({
            'offering': offering,
            'weekday_list': weekday_list,
        })
    
    print len(c_offerings)
    context.update({
        'offerings': c_offerings,
    })
    return render(request, template_name, context)

def subscription(request, course_id):
    template_name = "courses/subscription.html"
    context={}
    
    # clear session keys
    if 'user1_data' in request.session:
        del request.session['user1_data']
    if 'user2_data' in request.session:
        del request.session['user2_data']
    
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = UserForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            request.session['user1_data']=form.cleaned_data
            if not Course.objects.get(id=course_id).type.couple_course or ("subscribe_alone" in request.POST):
                return redirect('courses:subscription_do', course_id)
            elif "subscribe_partner" in request.POST:
                return redirect('courses:subscription2', course_id)
            else:
                return redirect('courses:subscription', course_id)

    # if a GET (or any other method) we'll create a blank form
    else:
        initial = {'newsletter': True}
        form = UserForm(initial=initial)

    context.update({
            'menu': "courses",
            'course': Course.objects.get(id=course_id),
            'person': 1,
            'form': form
        })
    return render(request, template_name, context)


def subscription2(request, course_id):
    template_name = "courses/subscription2.html"
    context={}
    
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = UserForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            request.session['user2_data']=form.cleaned_data
            return redirect('courses:subscription_do', course_id)

    # if a GET (or any other method) we'll create a blank form
    else:
        initial = {'newsletter': True}
        form = UserForm(initial=initial)

    context.update({
            'menu': "courses",
            'course': Course.objects.get(id=course_id),
            'person': 2,
            'form': form
        })
    return render(request, template_name, context)

def subscription_do(request, course_id):
    if 'user2_data' in request.session:
        res=services.subscribe(course_id,request.session['user1_data'], request.session['user2_data'])
    else:
        res=services.subscribe(course_id,request.session['user1_data'],None)
        
    # clear session keys
    if 'user1_data' in request.session:
        del request.session['user1_data']
    if 'user2_data' in request.session:
        del request.session['user2_data']
    
    request.session['subscription_result']=res
    return redirect('courses:subscription_done', course_id)

def subscription_done(request, course_id):
    template_name = "courses/subscription_done.html"
    context={}

    context.update({
            'menu': "courses",
            'message': request.session['subscription_result'],
            'course': Course.objects.get(id=course_id),
        })
    return render(request, template_name, context)

@login_required
def confirmation_check(request):
    template_name = "courses/confirmation_check.html"
    context={}
        
    context.update({
            'subscriptions': Subscribe.objects.filter(confirmed=True).select_related().filter(confirmations__isnull=True).all()
        })
    return render(request, template_name, context)

@login_required
def duplicate_users(request):
    template_name = "courses/duplicate_users.html"
    context={}
    users = []
    user_aliases = dict()
    duplicates=services.find_duplicate_users()
    for primary,aliases in duplicates.iteritems():
        users.append(User.objects.get(id=primary))
        user_aliases[primary]=User.objects.filter(id__in=aliases)
        
    context.update({
            'users': users,
            'user_aliases': user_aliases
        })
    return render(request, template_name, context)

from django.template.defaulttags import register

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
