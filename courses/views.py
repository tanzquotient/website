from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView, ListView
from django.core.exceptions import ObjectDoesNotExist

from django.utils.translation import ugettext as _

from django.contrib import messages
from django.contrib.auth.decorators import login_required

from models import *

from forms import *

import services

from django.contrib.auth.models import User
from django.utils import dateformat

import logging

log = logging.getLogger('tq')

# Create your views here.

def course_list(request):
    template_name = "courses/list.html"
    context = {}

    offerings = services.get_offerings_to_display()
    c_offerings = []
    for offering in offerings:
        offering_sections = []
        course_set = offering.course_set

        if offering.type == 'reg':
            for (w, w_name) in WEEKDAYS:
                section_dict = {}
                section_dict['section_title'] = WEEKDAYS_TRANS[w]
                section_dict['courses'] = [c for c in course_set.weekday(w) if c.is_displayed()]
                if (w == 'sat' or w == 'sun') and section_dict['courses'].__len__() == 0:
                    pass
                else:
                    offering_sections.append(section_dict)

            # add courses that have no weekday entry yet
            section_dict = {}
            section_dict['section_title'] = _("Unknown weekday")
            section_dict['courses'] = course_set.weekday(None)
            if section_dict['courses'].__len__() != 0:
                offering_sections.append(section_dict)
        elif offering.type == 'irr':
            courses_by_month = course_set.by_month()
            for (d, l) in sorted(courses_by_month.items()):
                if 1 < d.month < 12:
                    # use the django formatter for date objects
                    section_title = dateformat.format(d, 'F Y')
                else:
                    section_title = ""
                # tracks if at least one period of a course is set (it should be displayed on page)
                deviating_period = False
                for c in l:
                    if c.period:
                        deviating_period = True
                        break
                offering_sections.append(
                    {'section_title': section_title, 'courses': l, 'hide_period_column': not deviating_period})
        else:
            message = "unsupported offering type"
            log.error(message)
            raise Http404(message)

        c_offerings.append({
            'offering': offering,
            'sections': offering_sections,
        })

    context.update({
        'offerings': c_offerings,
    })
    return render(request, template_name, context)


def subscription(request, course_id):
    template_name = "courses/subscription.html"
    context = {}

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
            request.session['user1_data'] = form.cleaned_data
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
    context = {}

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = UserForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            request.session['user2_data'] = form.cleaned_data
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
        res = services.subscribe(course_id, request.session['user1_data'], request.session['user2_data'])
    else:
        res = services.subscribe(course_id, request.session['user1_data'], None)

    # clear session keys
    if 'user1_data' in request.session:
        del request.session['user1_data']
    if 'user2_data' in request.session:
        del request.session['user2_data']

    request.session['subscription_result'] = res
    return redirect('courses:subscription_done', course_id)


def subscription_done(request, course_id):
    template_name = "courses/subscription_done.html"
    context = {}

    context.update({
        'menu': "courses",
        'message': request.session['subscription_result'],
        'course': Course.objects.get(id=course_id),
    })
    return render(request, template_name, context)


@login_required
def confirmation_check(request):
    template_name = "courses/confirmation_check.html"
    context = {}

    context.update({
        'subscriptions': Subscribe.objects.filter(confirmed=True).select_related().filter(
            confirmations__isnull=True).all()
    })
    return render(request, template_name, context)


@login_required
def duplicate_users(request):
    template_name = "courses/duplicate_users.html"
    context = {}
    users = []
    user_aliases = dict()

    # if this is a POST request we need to process the form data
    if request.method == 'POST' and 'post' in request.POST and request.POST['post'] == 'yes':
        duplicates_ids = request.session['duplicates']
        to_merge = dict()
        for primary_id, aliases_ids in duplicates_ids.iteritems():
            to_merge_aliases = []
            for alias_id in aliases_ids:
                key = '{}-{}'.format(primary_id, alias_id)
                if key in request.POST and request.POST[key] == 'yes':
                    to_merge_aliases.append(alias_id)
            if to_merge_aliases:
                to_merge[primary_id] = to_merge_aliases
        log.info(to_merge)
        services.merge_duplicate_users_by_ids(to_merge)
    else:
        duplicates = services.find_duplicate_users()
        for primary, aliases in duplicates.iteritems():
            users.append(User.objects.get(id=primary))
            user_aliases[primary] = list(User.objects.filter(id__in=aliases))

        # for use when form is submitted
        request.session['duplicates'] = duplicates

    context.update({
        'users': users,
        'user_aliases': user_aliases
    })
    return render(request, template_name, context)


# helper function
def offering_place_chart_dict(offering):
    labels = []
    series_confirmed = []
    series_men_count = []
    series_women_count = []
    series_free = []
    courses = offering.course_set.all()

    for course in courses:
        labels.append(u'<a href="{}" target="_self">{}</a>'.format(reverse('courses:course_overview', args=[course.id]),
                                                                   course.name))
        series_confirmed.append(unicode(course.subscriptions.filter(confirmed=True).count()))
        mc = course.subscriptions.men().filter(confirmed=False).count()
        wc = course.subscriptions.women().filter(confirmed=False).count()
        series_men_count.append(unicode(mc))
        series_women_count.append(unicode(wc))
        freec = course.get_free_places_count()
        if freec:
            freec = max(0, freec - mc - wc)
        else:
            freec = 0
        series_free.append(unicode(freec))

    return {
        'labels': labels,
        'series_confirmed': series_confirmed,
        'series_men': series_men_count,
        'series_women': series_women_count,
        'series_free': series_free,
        'height': 25 * len(labels) + 90,
    }


# helper function
def offering_time_chart_dict(offering):
    traces = []
    for c in offering.course_set.all():
        trace = dict()
        trace['name'] = c.name
        trace['x'] = []
        trace['y'] = []
        counter = 0
        last = None
        for s in c.subscriptions.order_by('date').all():
            if last is None:
                last = s.date.date()
            if s.date.date() == last:
                counter += 1
            else:
                # save temp
                trace['x'].append(unicode(s.date.date()))
                trace['y'].append(counter)
                counter += 1
                last = s.date.date()
        if last is not None:
            trace['x'].append(unicode(last))
            trace['y'].append(counter)
        traces.append(trace)

    trace_total = dict()
    trace_total['x'] = []
    trace_total['y'] = []
    counter = 0
    last = None
    for s in Subscribe.objects.filter(course__offering__id=offering.id).order_by('date').all():
        if last is None:
            last = s.date.date()
        if s.date.date() == last:
            counter += 1
        else:
            # save temp
            print "add counter {}".format(counter)
            trace_total['x'].append(unicode(s.date.date()))
            trace_total['y'].append(counter)
            counter += 1
            last = s.date.date()
    if last is not None:
        trace_total['x'].append(unicode(last))
        trace_total['y'].append(counter)

    print trace_total['x']
    print trace_total['y']

    return {
        'traces': traces,
        'trace_total': trace_total,
    }


@login_required
def subscription_overview(request):
    template_name = "courses/auth/subscription_overview.html"
    context = {}

    offering_charts = []
    for o in services.get_offerings_to_display():
        offering_charts.append({'offering': o, 'place_chart': offering_place_chart_dict(o)})

    context.update({
        'offering_charts': offering_charts,
        'all_offerings': services.get_all_offerings()
    })
    return render(request, template_name, context)


@login_required
def course_overview(request, course_id):
    template_name = "courses/auth/course_overview.html"
    context = {}

    course = Course.objects.get(id=course_id)

    cc = course.subscriptions.filter(confirmed=True).count()
    mc = course.subscriptions.men().filter(confirmed=False).count()
    wc = course.subscriptions.women().filter(confirmed=False).count()
    freec = course.get_free_places_count()
    fc = freec - mc - wc if freec else 0

    context['course'] = course
    context['place_chart'] = {
        'label': course.name,
        'confirmed': cc,
        'men': mc,
        'women': wc,
        'free': fc,
        'total': cc + mc + wc + fc
    }
    return render(request, template_name, context)


@login_required
def offering_overview(request, offering_id):
    template_name = "courses/auth/offering_overview.html"
    context = {}

    o = Offering.objects.get(id=offering_id)

    context['offering'] = o
    context['place_chart'] = offering_place_chart_dict(o)
    context['time_chart'] = offering_time_chart_dict(o)
    return render(request, template_name, context)
