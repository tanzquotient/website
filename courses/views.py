import logging
from datetime import date
from typing import Type

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.db.models import Prefetch
from django.forms import Form
from django.http import Http404, HttpResponse, HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import FormView

from courses.forms import UserEditForm, create_initial_from_user, TeacherEditForm
from courses.utils import merge_duplicate_users, find_duplicate_users
from tq_website import settings
from utils.plots import plot_figure
from . import services, figures
from .forms.subscribe_form import SubscribeForm
from .models import Course, Style, Offering, OfferingType, Subscribe, IrregularLesson, \
    RegularLessonException
from .utils import course_filter

log = logging.getLogger('tq')


# Create your views here.

def course_list(request, subscription_type="all", style_name="all", force_preview=False) -> HttpResponse:
    template_name = "courses/list.html"

    # unpublished courses should be shown with a preview marker
    show_preview = (request and request.user.is_staff) or force_preview

    filter_styles = Style.objects.filter(filter_enabled=True)

    def matches_filter(c: Course) -> bool:
        return course_filter(c, show_preview, subscription_type, style_name, filter_styles)

    offerings = services.get_offerings_to_display(show_preview).prefetch_related(
        'period__cancellations',
        'course_set__type',
        'course_set__period__cancellations',
        'course_set__regular_lessons',
        'course_set__room__address',
        'course_set__room__translations',
        Prefetch('course_set__irregular_lessons', queryset=IrregularLesson.objects.order_by('date', 'time_from')),
        Prefetch('course_set__regular_lessons__exceptions', queryset=RegularLessonException.objects.order_by('date')),
        Prefetch('course_set__subscriptions', queryset=Subscribe.objects.active(), to_attr='active_subscriptions'),
        'course_set__subscriptions',
    )

    c_offerings = []
    for offering in offerings:
        offering_sections = services.get_sections(offering, matches_filter)

        if offering_sections:
            c_offerings.append({
                'offering': offering,
                'sections': offering_sections,
            })

    # Courses without offering -> create fake offering
    courses_without_offering = list(filter(matches_filter, services.get_upcoming_courses_without_offering()))
    if courses_without_offering:
        courses_without_offering.sort(key=lambda c: c.get_first_lesson_date() or date.min)

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


def archive(request: HttpRequest) -> HttpResponse:
    template_name = "courses/archive.html"
    context = {
        'historic_offerings': {
            "regular": services.get_historic_offerings(offering_type=OfferingType.REGULAR),
            "irregular": services.get_historic_offerings(offering_type=OfferingType.IRREGULAR),
        },
    }
    return render(request, template_name, context)


@staff_member_required
def course_list_preview(request) -> HttpResponse:
    return course_list(request, force_preview=True)


def offering_by_id(request: HttpRequest, offering_id: int) -> HttpResponse:
    template_name = 'courses/offering.html'
    offering = get_object_or_404(Offering.objects, id=offering_id)
    if not offering.is_public():
        raise Http404()
    context = {
        "offering": offering,
        "sections": services.get_sections(offering)
    }
    return render(request, template_name, context)


def course_detail(request: HttpRequest, course_id: int) -> HttpResponse:
    context = {
        'menu': "courses",
        'course': get_object_or_404(Course.objects, id=course_id),
        'user': request.user
    }
    return render(request, "courses/course_detail.html", context)


@login_required
def subscribe_form(request: HttpRequest, course_id: int) -> HttpResponse:
    course = get_object_or_404(Course.objects, id=course_id)

    # If user already signed up or sign up not possible: redirect to course detail
    if course.subscriptions.filter(user=request.user).exists() \
            or (not course.is_subscription_allowed() and not request.user.is_staff)  \
            or not course.has_free_places:
        return redirect('courses:course_detail', course_id=course_id)

    # If user is has overdue payments -> block subscribing to new courses
    if request.user.profile.subscriptions_with_overdue_payment():
        return render(request, "courses/overdue_payments.html", dict(
            email_address=settings.EMAIL_ADDRESS_FINANCES,
            payment_account=settings.PAYMENT_ACCOUNT['default']
        ))

    # Get form
    form_data = request.POST if request.method == 'POST' else None
    form = SubscribeForm(user=request.user, course=course, data=form_data)

    # Sign up user for course if form is valid
    if form.is_valid():
        subscription = services.subscribe(course, request.user, form.cleaned_data)
        context = {
            'course': course,
            'subscription': subscription,
        }
        return render(request, "courses/course_subscribe_status.html", context=context)

    # Render sign up form
    context = {
        'course': course,
        'form': form
    }
    return render(request, "courses/course_subscribe_form.html", context)


@staff_member_required
def confirmation_check(request: HttpRequest) -> HttpResponse:
    template_name = "courses/confirmation_check.html"
    context = {}

    context.update({
        'subscriptions': Subscribe.objects.accepted().select_related().filter(
            confirmations__isnull=True).all()
    })
    return render(request, template_name, context)


@staff_member_required
def duplicate_users(request: HttpRequest) -> HttpResponse:
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


def offering_place_chart_dict(offering: Offering) -> dict:
    labels = []
    series_confirmed = []
    series_matched = []
    series_leaders_count = []
    series_followers_count = []
    series_no_preference_count = []
    series_free = []
    courses = offering.course_set.reverse().all()

    for course in courses:
        # NOTE: do not use the related manager with 'course.subscriptions',
        # because does not have access to default manager methods
        subscriptions = Subscribe.objects.filter(course=course)
        labels.append(u'<a href="{}">{}</a>'.format(reverse('courses:course_overview', args=[course.id]),
                                                    escape(course.name)))

        total_count = subscriptions.active().count()
        confirmed_count = subscriptions.accepted().count()
        matched_count = subscriptions.new().matched().count()
        leaders_count = subscriptions.new().single().leaders().count()
        followers_count = subscriptions.new().single().followers().count()
        no_preference_count = total_count - matched_count - confirmed_count - leaders_count - followers_count
        maximum = course.max_subscribers
        if maximum:
            free_count = max(0, maximum - total_count)
        else:
            free_count = 0

        series_confirmed.append(str(confirmed_count))
        series_matched.append(str(matched_count))
        series_leaders_count.append(str(leaders_count))
        series_followers_count.append(str(followers_count))
        series_no_preference_count.append(str(no_preference_count))

        series_free.append(str(free_count))

    return {
        'labels': labels,
        'series_confirmed': series_confirmed,
        'series_matched': series_matched,
        'series_leaders': series_leaders_count,
        'series_followers': series_followers_count,
        'series_no_preference': series_no_preference_count,
        'series_free': series_free,
        'height': 25 * len(labels) + 90,
    }

# helper function


def offering_time_chart_dict(offering: Offering) -> dict:
    traces = []
    for c in offering.course_set.reverse().all():
        trace = dict()
        trace['name'] = c.name
        values = dict()
        for s in c.subscriptions.all():
            key = str(s.date.date())
            values[key] = values.get(key, 0) + 1

        tuples = [(x, y) for x, y in values.items()]

        trace['x'] = [x for x, _ in tuples]
        trace['y'] = [y for _, y in tuples]

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
            trace_total['x'].append(str(last))
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
def subscription_overview(request: HttpRequest) -> HttpResponse:
    offering_charts = []
    for o in services.get_offerings_to_display():
        offering_charts.append({'offering': o, 'place_chart': offering_place_chart_dict(o)})

    context = {
        'offering_charts': offering_charts,
        'all_offerings': services.get_all_offerings(),
        'offering_state_status_chart': plot_figure(figures.offering_state_status()),
        'offering_matching_status_chart': plot_figure(figures.offering_matching_status()),
        'offering_by_student_status_chart': plot_figure(figures.offering_by_student_status()),
        'offering_lead_follow_couple_chart': plot_figure(figures.offering_lead_follow_couple()),
    }
    return render(request, "courses/auth/subscription_overview.html", context)


@staff_member_required
def course_overview(request: HttpRequest, course_id: int) -> HttpResponse:
    template_name = "courses/auth/course_overview.html"
    context = {}

    course = Course.objects.get(id=course_id)
    # NOTE: do not use the related manager with 'course.subscriptions',
    # because does not have access to default manager methods
    subscriptions = Subscribe.objects.filter(course=course)

    total_count = subscriptions.active().count()
    confirmed_count = subscriptions.accepted().count()
    matched_count = subscriptions.new().matched().count()
    leaders_count = subscriptions.new().single().leaders().count()
    followers_count = subscriptions.new().single().followers().count()
    no_preference_count = total_count - matched_count - confirmed_count - leaders_count - followers_count

    maximum = course.max_subscribers
    if maximum:
        free_count = max(0, maximum - total_count)
    else:
        free_count = 0

    context['course'] = course
    context['place_chart'] = {
        'label': course.name,
        'confirmed': confirmed_count,
        'matched': matched_count,
        'leaders': leaders_count,
        'followers': followers_count,
        'no_preference': no_preference_count,
        'free': free_count,
        'total': total_count
    }
    return render(request, template_name, context)


@staff_member_required
def offering_overview(request: HttpRequest, offering_id: int) -> HttpResponse:
    template_name = "courses/auth/offering_overview.html"
    context = {}

    o = Offering.objects.get(id=offering_id)

    context['offering'] = o
    context['place_chart'] = offering_place_chart_dict(o)
    context['time_chart'] = offering_time_chart_dict(o)
    return render(request, template_name, context)


@login_required
def user_courses(request: HttpRequest) -> HttpResponse:
    template_name = "user/user_courses.html"
    context = {
        'user': request.user,
        'payment_account': settings.PAYMENT_ACCOUNT['default']
    }
    return render(request, template_name, context)


@login_required
def user_profile(request: HttpRequest) -> HttpResponse:
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

    def get_form_class(self) -> Type[Form]:
        if self.request.user.profile.is_teacher():
            return TeacherEditForm
        return super().get_form_class()

    def get_initial(self) -> dict:
        initial = create_initial_from_user(self.request.user)
        return initial

    def get_context_data(self, **kwargs) -> dict:
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

    def form_valid(self, form) -> HttpResponse:
        services.update_user(self.request.user, form.cleaned_data)
        return super(ProfileView, self).form_valid(form)


@login_required
def change_password(request: HttpRequest) -> HttpResponse:
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
def export_summary(request: HttpRequest) -> HttpResponse:
    from courses import services
    return services.export_summary('csv')


@staff_member_required
def export_summary_excel(request: HttpRequest) -> HttpResponse:
    from courses import services
    return services.export_summary('xlsx')


@staff_member_required
def export_offering_summary(request: HttpRequest, offering_id: int) -> HttpResponse:
    from courses import services
    return services.export_summary('csv', [Offering.objects.filter(pk=offering_id).first()])


@staff_member_required
def export_offering_summary_excel(request: HttpRequest, offering_id: int) -> HttpResponse:
    from courses import services
    return services.export_summary('xlsx', [Offering.objects.filter(pk=offering_id).first()])


@staff_member_required
def export_offering_teacher_payment_information(request: HttpRequest, offering_id: int) -> HttpResponse:
    from courses import services
    return services.export_teacher_payment_information('csv', [Offering.objects.filter(pk=offering_id).first()])


@staff_member_required
def export_offering_teacher_payment_information_excel(request: HttpRequest, offering_id: int) -> HttpResponse:
    from courses import services
    return services.export_teacher_payment_information('xlsx', [Offering.objects.filter(pk=offering_id).first()])
