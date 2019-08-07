import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.sessions.exceptions import SuspiciousSession
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import dateformat
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.utils.html import escape
from django.views.generic.edit import FormView

from courses.forms import UserEditForm, create_initial_from_user, TeacherEditForm
from courses.utils import merge_duplicate_users, find_duplicate_users
from tq_website import settings
from . import services
from .models import *
from .utils import course_filter

log = logging.getLogger('tq')


# Create your views here.

def course_list(request, subscription_type="all", style_name="all", force_preview=False):
    template_name = "courses/list.html"

    # unpublished courses should be shown with a preview marker
    preview_mode = request and request.user.is_staff or force_preview

    filter_styles = Style.objects.filter(filter_enabled=True)

    def matches_filter(c):
        return course_filter(c, preview_mode, subscription_type, style_name, filter_styles)

    offerings = services.get_offerings_to_display(request, preview_mode)
    c_offerings = []
    for offering in offerings:
        offering_sections = []
        course_set = offering.course_set

        if offering.type == OfferingType.REGULAR:
            for (w, w_name) in Weekday.CHOICES:
                courses_on_weekday = [c for c in course_set.weekday(w) if matches_filter(c)]
                if courses_on_weekday:
                    offering_sections.append({
                        'section_title': Weekday.WEEKDAYS_TRANSLATIONS_DE[w],
                        'courses': courses_on_weekday
                    })

            courses_without_weekday = [c for c in course_set.weekday(None) if matches_filter(c)]
            if courses_without_weekday:
                offering_sections.append({'section_title': _("Irregular weekday"), 'courses': courses_without_weekday})

        elif offering.type == OfferingType.IRREGULAR:
            courses_by_month = course_set.by_month()
            for (d, courses) in courses_by_month:
                if d is None:
                    section_title = _("Unknown month")
                elif 1 < d.month < 12:
                    # use the django formatter for date objects
                    section_title = dateformat.format(d, 'F Y')
                else:
                    section_title = ""
                # filter out undisplayed courses if not staff user
                courses = [c for c in courses if matches_filter(c)]
                # tracks if at least one period of a course is set (it should be displayed on page)
                deviating_period = False
                for c in courses:
                    if c.period:
                        deviating_period = True
                        break

                if courses:
                    offering_sections.append(
                        {'section_title': section_title, 'courses': courses, 'hide_period_column': not deviating_period})
        else:
            message = "unsupported offering type"
            log.error(message)
            raise Http404(message)

        if offering_sections:
            c_offerings.append({
                'offering': offering,
                'sections': offering_sections,
            })

    # Courses without offering -> create fake offering
    courses_without_offering = list(filter(matches_filter, services.get_upcoming_courses_without_offering()))
    if courses_without_offering:
        courses_without_offering.sort(key=lambda c: c.get_first_lesson_date())

        c_offerings.insert(0, {
            'offering': {
                'name': _("Upcoming courses"),
                'type': OfferingType.IRREGULAR,
                'display': True,
                'active': True,
            },
            'sections': [
                {
                    'section_title': _("Next courses"),
                    'courses': courses_without_offering
                }
            ]
        })

    context = {
        'offerings': c_offerings,
        'filter': {
            'styles': {
                'available': filter_styles,
                'selected': style_name,
            },
            'subscription_type': subscription_type,
        }
    }
    return render(request, template_name, context)


@staff_member_required
def course_list_preview(request):
    return course_list(request, force_preview=True)


def subscription(request, course_id):
    """
    This view provides a form to enrol in a course

    Redirects:
    courses:course_list         if no course with the given ID exists
    courses:subscription        if no valid submit button value is found
    courses:subscription_do     everything is ok, redirection to actually perform the enrolment
    """
    from .forms import SingleSubscriptionForm, CoupleSubscriptionForm
    template_name = "courses/subscription.html"

    # do not clear session keys
    course = Course.objects.filter(id=course_id)

    # if there is no course with this id --> redirect user to course list
    if len(course) == 0:
        return redirect('courses:list')
    # the course id must be unique; this is a consistency check
    assert len(course) == 1
    course = course[0]

    is_couple_course = course.type.couple_course

    # create the correct form instance
    if is_couple_course:
        form = CoupleSubscriptionForm(request.POST)
    else:
        form = SingleSubscriptionForm(request.POST)

    # if this is a POST request we need to process the form data
    if request.method == 'POST':

        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            assert request.user != None
            data = {
                'user_id1': request.user.id,
                'experience': form.cleaned_data['experience'],
                'comment': form.cleaned_data['comment'],
            }
            if 'partner_email' in form.cleaned_data and form.cleaned_data['partner_email']:
                partner = UserProfile.objects.filter(user__email=form.cleaned_data['partner_email'])
                assert len(partner) == 1  # there should only be one partner with this email address
                partner = partner[0]
                data['user_id2'] = partner.user.id

            request.session['data'] = data
            if 'subscribe' in request.POST:
                return redirect('courses:subscription_do', course_id)
            else:
                # no valid submit button value
                return redirect('courses:subscription', course_id)

    context = {}
    context.update({
        'menu': "courses",
        'course': get_object_or_404(Course, id=course_id),
        'form': form
    })
    return render(request, template_name, context)


@login_required
def subscription_do(request, course_id):
    """
    This view actually performs the enrolment in a given course.

    The view is just a wrapper to call services.subscribe(...)
    Redirects:
    courses:subscription_message    always in order to inform the user about success of enrolment
    """
    if 'data' not in request.session:
        raise SuspiciousSession()

    res = services.subscribe(course_id, request.session['data'])

    # clear session keys
    if 'data' in request.session:
        del request.session['data']

    request.session['subscription_result'] = res
    return redirect('courses:subscription_message', course_id)


def subscription_message(request, course_id):
    """
    This view displays whether the enrolment was successful or not

    Redirects:
    courses:subscription    if there is no result in the given request
    """
    if 'subscription_result' not in request.session:
        return redirect('courses:subscription', course_id)

    template_name = "courses/subscription_message.html"
    context = {}

    context.update({
        'menu': "courses",
        'message': request.session['subscription_result'],
        'course': Course.objects.get(id=course_id),
    })
    return render(request, template_name, context)


@staff_member_required
def confirmation_check(request):
    template_name = "courses/confirmation_check.html"
    context = {}

    context.update({
        'subscriptions': Subscribe.objects.accepted().select_related().filter(
            confirmations__isnull=True).all()
    })
    return render(request, template_name, context)


@staff_member_required
def duplicate_users(request):
    template_name = "courses/duplicate_users.html"
    context = {}
    users = []
    user_aliases = dict()

    # if this is a POST request we need to process the form data
    if request.method == 'POST' and 'post' in request.POST and request.POST['post'] == 'yes':
        duplicates_ids = request.session['duplicates']
        to_merge = dict()
        for primary_id, aliases_ids in duplicates_ids.items():
            to_merge_aliases = []
            for alias_id in aliases_ids:
                key = '{}-{}'.format(primary_id, alias_id)
                if key in request.POST and request.POST[key] == 'yes':
                    to_merge_aliases.append(alias_id)
            if to_merge_aliases:
                to_merge[primary_id] = to_merge_aliases
        log.info(to_merge)
        merge_duplicate_users(to_merge)
    else:
        duplicates = find_duplicate_users()
        for primary, aliases in duplicates.items():
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
        # NOTE: do not use the related manager with 'course.subscriptions',
        # because does not have access to default manager methods
        subscriptions = Subscribe.objects.filter(course=course)
        labels.append(u'<a href="{}">{}</a>'.format(reverse('courses:course_overview', args=[course.id]),
                                                    escape(course.name)))
        accepted_count = subscriptions.accepted().count()
        series_confirmed.append(str(accepted_count))
        mc = subscriptions.new().men().count()
        wc = subscriptions.new().women().count()
        series_men_count.append(str(mc))
        series_women_count.append(str(wc))
        maximum = course.max_subscribers
        if maximum:
            freec = max(0, maximum - accepted_count - mc - wc)
        else:
            freec = 0
        series_free.append(str(freec))

    return {
        'labels': labels,
        'series_confirmed': series_confirmed,
        'series_men': series_men_count,
        'series_women': series_women_count,
        'series_free': series_free,
        'height': 25 * len(labels) + 90,
    }


def progress_chart_dict():
    labels = []
    series_couple = []
    series_single = []

    for o in Offering.objects.filter(type=OfferingType.REGULAR).all():
        subscriptions = Subscribe.objects.filter(course__offering=o)
        labels.append(u'<a href="{}">{}</a>'.format(reverse('courses:offering_overview', args=[o.id]),
                                                    escape(o.name)))
        accepted = subscriptions.accepted()
        total_count = accepted.count()
        couple_count = accepted.filter(matching_state=MatchingState.COUPLE).count()
        single_count = total_count - couple_count

        series_couple.append(str(couple_count))
        series_single.append(str(single_count))

    return {
        'labels': labels,
        'series_couple': series_couple,
        'series_single': series_single,
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
                trace['x'].append(str(s.date.date()))
                trace['y'].append(counter)
                counter += 1
                last = s.date.date()
        if last is not None:
            trace['x'].append(str(last))
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
            print("add counter {}".format(counter))
            trace_total['x'].append(str(s.date.date()))
            trace_total['y'].append(counter)
            counter += 1
            last = s.date.date()
    if last is not None:
        trace_total['x'].append(str(last))
        trace_total['y'].append(counter)

    print(trace_total['x'])
    print(trace_total['y'])

    return {
        'traces': traces,
        'trace_total': trace_total,
    }


@staff_member_required
def subscription_overview(request):
    template_name = "courses/auth/subscription_overview.html"
    context = {}

    offering_charts = []
    for o in services.get_offerings_to_display(request):
        offering_charts.append({'offering': o, 'place_chart': offering_place_chart_dict(o)})

    ETH_count = len(Subscribe.objects.filter(user__profile__student_status=StudentStatus.ETH))
    UZH_count = len(Subscribe.objects.filter(user__profile__student_status=StudentStatus.UNI))
    PH_count = len(Subscribe.objects.filter(user__profile__student_status=StudentStatus.PH))
    other_count = len(Subscribe.objects.filter(user__profile__student_status=StudentStatus.OTHER))
    no_count = len(Subscribe.objects.filter(user__profile__student_status=StudentStatus.NO))

    university_chart = {
        'ETH_count': ETH_count,
        'UZH_count': UZH_count,
        'PH_count': PH_count,
        'no_count': no_count,
        'other_count': other_count,
    }

    context.update({
        'progress_chart': progress_chart_dict(),
        'offering_charts': offering_charts,
        'all_offerings': services.get_all_offerings(),
        'university_chart': university_chart
    })
    return render(request, template_name, context)


@staff_member_required
def course_overview(request, course_id):
    template_name = "courses/auth/course_overview.html"
    context = {}

    course = Course.objects.get(id=course_id)
    # NOTE: do not use the related manager with 'course.subscriptions',
    # because does not have access to default manager methods
    subscriptions = Subscribe.objects.filter(course=course)

    cc = subscriptions.accepted().count()
    mc = subscriptions.new().men().count()
    wc = subscriptions.new().women().count()
    maximum = course.max_subscribers
    if maximum:
        freec = max(0, maximum - cc - mc - wc)
    else:
        freec = 0

    context['course'] = course
    context['place_chart'] = {
        'label': course.name,
        'confirmed': cc,
        'men': mc,
        'women': wc,
        'free': freec,
        'total': cc + mc + wc + freec
    }
    return render(request, template_name, context)


@staff_member_required
def offering_overview(request, offering_id):
    template_name = "courses/auth/offering_overview.html"
    context = {}

    o = Offering.objects.get(id=offering_id)

    context['offering'] = o
    context['place_chart'] = offering_place_chart_dict(o)
    context['time_chart'] = offering_time_chart_dict(o)
    return render(request, template_name, context)


@login_required
def user_dashboard(request):
    template_name = "user/dashboard.html"
    context = {
        'user': request.user,
        'payment_account': settings.PAYMENT_ACCOUNT['default']
    }
    return render(request, template_name, context)


@login_required
def user_profile(request):
    template_name = "user/profile.html"
    context = {
        'user': request.user
    }
    return render(request, template_name, context)


@method_decorator(login_required, name='dispatch')
class ProfileView(FormView):
    template_name = 'courses/auth/profile.html'
    form_class = UserEditForm
    success_url = reverse_lazy('edit_profile')

    def get_form_class(self):
        if self.request.user.profile.is_teacher():
            return TeacherEditForm
        return super().get_form_class()

    def get_initial(self):
        initial = create_initial_from_user(self.request.user)
        return initial

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ProfileView, self).get_context_data(**kwargs)

        user = self.request.user
        if user.profile.gender:
            context['gender_icon'] = 'mars' if user.profile.gender == 'm' else 'venus'
        context['is_teacher'] = user.profile.is_teacher()
        context['is_board_member'] = user.profile.is_board_member()
        context['is_profile_complete'] = user.profile.is_complete()
        context['profile_missing_values'] = user.profile.missing_values()
        return context

    def form_valid(self, form):
        services.update_user(self.request.user, form.cleaned_data)
        return super(ProfileView, self).form_valid(form)


@login_required
def change_password(request):
    success = True
    initial = True
    if request.method == 'POST':
        initial = False
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
        else:
            success = False
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'account/change_password.html', {
        'form': form,
        'success': success,
        'initial': initial,
    })


@staff_member_required
def export_summary(request):
    from courses import services
    return services.export_summary('csv')


@staff_member_required
def export_summary_excel(request):
    from courses import services
    return services.export_summary('xlsx')


@staff_member_required
def export_offering_summary(request, offering_id):
    from courses import services
    return services.export_summary('csv', [Offering.objects.filter(pk=offering_id).first()])


@staff_member_required
def export_offering_summary_excel(request, offering_id):
    from courses import services
    return services.export_summary('xlsx', [Offering.objects.filter(pk=offering_id).first()])


@staff_member_required
def export_offering_teacher_payment_information(request, offering_id):
    from courses import services
    return services.export_teacher_payment_information('csv', [Offering.objects.filter(pk=offering_id).first()])


@staff_member_required
def export_offering_teacher_payment_information_excel(request, offering_id):
    from courses import services
    return services.export_teacher_payment_information('xlsx', [Offering.objects.filter(pk=offering_id).first()])
