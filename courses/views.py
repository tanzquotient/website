import hashlib
import logging
import os
from datetime import timedelta

import pytz
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.syndication.views import add_domain
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.views.generic.edit import FormView
from icalendar import Calendar, Event, vDatetime, vDuration, vText

from courses.forms import UserEditForm, create_initial_from_user
from courses.models.choices import SubscribeState
from courses.utils import find_duplicate_users, merge_duplicate_users
from tq_website import settings
from utils.plots import plot_figure
from utils.tables.table_view_or_export import table_view_or_export
from . import figures, services
from .forms.subscribe_form import SubscribeForm
from .models import (
    Course,
    IrregularLesson,
    Offering,
    OfferingType,
    RegularLessonException,
    Style,
    Subscribe,
    RejectionReason,
    MatchingState,
    UserProfile,
    LessonOccurrence,
)
from .services.data.teachers_overview import get_teachers_overview_data
from .utils import course_filter

log = logging.getLogger("tq")


# Create your views here.


@cache_page(5 * 60)
@vary_on_cookie
def course_list(
    request, subscription_type="all", style_name="all", show_preview=False
) -> HttpResponse:
    template_name = "courses/list.html"

    context = course_list_context(
        subscription_type=subscription_type,
        style_name=style_name,
        show_preview=show_preview,
    )
    return render(request, template_name, context)


def course_list_context(
    subscription_type="all", style_name="all", show_preview=False
) -> dict:
    filter_styles = Style.objects.filter(filter_enabled=True)

    def matches_filter(c: Course) -> bool:
        return course_filter(
            c, show_preview, subscription_type, style_name, filter_styles
        )

    offerings = services.get_offerings_to_display(show_preview).prefetch_related(
        "period__cancellations",
        "course_set",
        "course_set__type",
        "course_set__type__translations",
        "course_set__period__cancellations",
        "course_set__room",
        "course_set__room__cancellations",
        "course_set__regular_lessons",
        "course_set__room__address",
        "course_set__room__translations",
        "course_set__lesson_occurrences",
        Prefetch(
            "course_set__irregular_lessons",
            queryset=IrregularLesson.objects.order_by("date", "time_from"),
        ),
        Prefetch(
            "course_set__regular_lessons__exceptions",
            queryset=RegularLessonException.objects.order_by("date"),
        ),
        Prefetch(
            "course_set__subscriptions",
            queryset=Subscribe.objects.active(),
            to_attr="active_subscriptions",
        ),
        "course_set__subscriptions",
    )
    c_offerings = []
    for offering in offerings:
        offering_sections = services.get_sections(offering, matches_filter)

        if offering_sections:
            c_offerings.append(
                {
                    "offering": offering,
                    "sections": offering_sections,
                }
            )
    context = {
        "offerings": c_offerings,
        "filter": {
            "styles": {
                "available": filter_styles,
                "selected": style_name,
            },
            "subscription_type": subscription_type,
        },
    }
    return context


@cache_page(60 * 60)
def archive(request: HttpRequest) -> HttpResponse:
    template_name = "courses/archive.html"
    context = dict()
    return render(request, template_name, context)


@staff_member_required
def course_list_preview(request) -> HttpResponse:
    return course_list(request, show_preview=True)


@cache_page(5 * 60)
@vary_on_cookie
def offering_by_id(request: HttpRequest, offering_id: int) -> HttpResponse:
    template_name = "courses/offering.html"
    offering = get_object_or_404(Offering.objects, id=offering_id)
    if not offering.is_public():
        raise Http404()
    context = {
        "offering": offering,
        "sections": services.get_sections(offering),
        "limit_per_section": offering.course_set.count(),
    }
    return render(request, template_name, context)


def course_detail(request: HttpRequest, course_id: int) -> HttpResponse:
    try:
        course = (
            Course.objects.select_related("type", "offering")
            .prefetch_related(
                "subscriptions",
                "type__styles__translations",
                "regular_lessons__exceptions",
                "irregular_lessons",
                "teaching__teacher__functions",
                "teaching__teacher__profile",
                "teaching__teacher__teaching_courses__course__lesson_occurrences",
                "teaching__teacher__teaching_courses__course__irregular_lessons",
                "teaching__teacher__teaching_courses__course__regular_lessons",
                "teaching__teacher__teaching_courses__course__period",
                "teaching__teacher__teaching_courses__course__offering__period",
            )
            .get(id=course_id)
        )
    except Course.DoesNotExist:
        raise Http404()

    context = {
        "menu": "courses",
        "course": course,
        "user": request.user,
    }
    return render(request, "courses/course_detail.html", context)


def _lesson_to_ical_event(
    course: Course,
    lesson_occurrence: LessonOccurrence,
    request: HttpRequest,
    subscription: Subscribe = None,
):
    event = Event()
    event["dtstart"] = vDatetime(timezone.localtime(lesson_occurrence.start, pytz.UTC))
    event["dtend"] = vDatetime(timezone.localtime(lesson_occurrence.end, pytz.UTC))

    course_title = course.type.title
    event_title = course_title
    tentative = False
    if subscription:
        if subscription.state == SubscribeState.WAITING_LIST:
            event_title = f"[{_('Waiting list')}] {course_title}"
            tentative = True
        elif subscription.state not in SubscribeState.ACCEPTED_STATES:
            event_title = f"[{_('Tentative')}] {course_title}"
            tentative = True

    event.add("summary", vText(event_title))
    if tentative:
        event.add("status", vText("TENTATIVE"))
    event.add("location", vText(lesson_occurrence.room or course.room))
    event.add(
        "description",
        "\n\n".join(
            [
                strip_tags(string)
                for string in [
                    course.safe_translation_getter("description"),
                    course.type.safe_translation_getter("description"),
                    course.format_prices(),
                    (
                        f"{_('Teachers')}: {course.format_teachers}"
                        if course.get_teachers()
                        else None
                    ),
                ]
                if string
            ]
        ),
    )
    event.add(
        "url",
        add_domain(
            get_current_site(request),
            reverse("courses:course_detail", kwargs=dict(course_id=course.id)),
            request.is_secure(),
        ),
    )

    # Attendees:
    # Could possibly add teachers, students, etc.
    # However, exposing the E-Mail is not ok, and attendees don't exist without,
    # so we don't add any attendees. If we did, the code would look like this:
    # for teacher in course.get_teachers():
    #     if teacher.email is not None:
    #         attendee = vCalAddress("MAILTO:{}".format(teacher.email))
    #         attendee.params['cn'] = vText(teacher.first_name + " "  + teacher.last_name)
    #         attendee.params['ROLE'] = vText('Teacher')
    #         event.add('attendee', attendee, encode=0)

    return event


def course_ical(request: HttpRequest, course_id: int) -> HttpResponse:
    cache_key = f"course_ical_{course_id}"
    response = cache.get(cache_key)
    if response:
        return response

    course: Course = get_object_or_404(Course.objects, id=course_id)
    cal = Calendar()
    cal.add("version", "2.0")
    cal.add("prodid", f"-//Tanzquotient calendar for course {course_id}//mxm.dk//")
    cal.add("name", course.type.title)
    for occurrence in course.lesson_occurrences.all():
        event = _lesson_to_ical_event(course, occurrence, request)
        cal.add_component(event)

    response = HttpResponse(cal.to_ical(), content_type="text/calendar")
    cache.set(cache_key, response, 60 * 60 * 24)
    return response


@login_required
def subscribe_form(request: HttpRequest, course_id: int) -> HttpResponse:
    course: Course = get_object_or_404(Course.objects, id=course_id)

    # If user already signed up or sign up not possible: redirect to course detail
    if not course.user_can_subscribe(request.user):
        return redirect("courses:course_detail", course_id=course_id)

    # If user has overdue payments -> block subscribing to new courses
    if request.user.profile.subscriptions_with_overdue_payment():
        return render(
            request,
            "courses/overdue_payments.html",
            dict(
                email_address=settings.EMAIL_ADDRESS_FINANCES,
                payment_account=settings.PAYMENT_ACCOUNT["default"],
            ),
        )

    # Get form
    form_data = request.POST if request.method == "POST" else None
    form = SubscribeForm(user=request.user, course=course, data=form_data)

    # Sign up user for course if form is valid
    if form.is_valid():
        subscription = services.subscribe(course, request.user, form.cleaned_data)
        context = {
            "course": course,
            "subscription": subscription,
            "waiting_list": subscription.state == SubscribeState.WAITING_LIST,
        }
        return render(request, "courses/course_subscribe_status.html", context=context)

    # Render sign up form

    past_partners = sorted(
        list(
            {
                (subscribe.partner.get_full_name(), subscribe.partner.email)
                for subscribe in request.user.subscriptions.all()
                if subscribe.partner
            }
        )
    )

    context = {
        "course": course,
        "form": form,
        "past_partners": past_partners,
    }
    return render(request, "courses/course_subscribe_form.html", context)


@staff_member_required
def confirmation_check(request: HttpRequest) -> HttpResponse:
    template_name = "courses/confirmation_check.html"
    context = {}

    context.update(
        {
            "subscriptions": Subscribe.objects.accepted()
            .select_related()
            .filter(confirmations__isnull=True)
            .all()
        }
    )
    return render(request, template_name, context)


@staff_member_required
def duplicate_users(request: HttpRequest) -> HttpResponse:
    template_name = "courses/duplicate_users.html"
    context = {}
    users = []
    user_aliases = dict()

    # if this is a POST request we need to process the form data
    if (
        request.method == "POST"
        and "post" in request.POST
        and request.POST["post"] == "yes"
    ):
        duplicates_ids = request.session["duplicates"]
        to_merge = dict()
        for primary_id, aliases_ids in duplicates_ids.items():
            to_merge_aliases = []
            for alias_id in aliases_ids:
                key = "{}-{}".format(primary_id, alias_id)
                if key in request.POST and request.POST[key] == "yes":
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
        request.session["duplicates"] = duplicates

    context.update({"users": users, "user_aliases": user_aliases})
    return render(request, template_name, context)


def offering_time_chart_dict(offering: Offering) -> dict:
    traces = []
    for c in offering.course_set.reverse().all():
        trace = dict()
        trace["name"] = c.name
        values = dict()
        for s in c.subscriptions.all():
            key = str(s.date.date())
            values[key] = values.get(key, 0) + 1

        tuples = [(x, y) for x, y in values.items()]

        trace["x"] = [x for x, _ in tuples]
        trace["y"] = [y for _, y in tuples]

        traces.append(trace)

    trace_total = dict()
    trace_total["x"] = []
    trace_total["y"] = []
    counter = 0
    last = None

    for s in (
        Subscribe.objects.filter(course__offering__id=offering.id)
        .order_by("date")
        .all()
    ):
        if last is None:
            last = s.date.date()
        if s.date.date() == last:
            counter += 1
        else:
            # save temp
            print("add counter {}".format(counter))
            trace_total["x"].append(str(last))
            trace_total["y"].append(counter)
            counter += 1
            last = s.date.date()
    if last is not None:
        trace_total["x"].append(str(last))
        trace_total["y"].append(counter)

    print(trace_total["x"])
    print(trace_total["y"])

    return {
        "traces": traces,
        "trace_total": trace_total,
    }


@staff_member_required
def teachers_overview(request: HttpRequest) -> HttpResponse:
    return table_view_or_export(
        request,
        _("Teachers overview"),
        "courses:teachers_overview",
        get_teachers_overview_data(),
    )


@staff_member_required
def subscription_overview(request: HttpRequest) -> HttpResponse:
    figure_types = dict(
        status=dict(
            title=_("By subscription status"), plot=figures.offering_state_status
        ),
        affiliation=dict(
            title=_("By affiliation"), plot=figures.offering_by_student_status
        ),
        matching=dict(
            title=_("By matching states"), plot=figures.offering_matching_status
        ),
        lead_follow=dict(
            title=_("By lead and follow"), plot=figures.offering_lead_follow_couple
        ),
    )
    figure_type: str = (
        request.GET["figure_type"] if "figure_type" in request.GET else "status"
    )
    return render(
        request,
        "courses/auth/subscription_overview.html",
        dict(
            figure_type=figure_type,
            figure_types=[(k, v["title"]) for k, v in figure_types.items()],
            plots={
                offering_type: plot_figure(
                    figure_types[figure_type]["plot"](offering_type)
                )
                for offering_type in [OfferingType.REGULAR, OfferingType.IRREGULAR]
            },
        ),
    )


@staff_member_required
def offering_overview(request: HttpRequest, offering_id: int) -> HttpResponse:
    template_name = "courses/auth/offering_overview.html"
    context = {}

    offering = Offering.objects.get(id=offering_id)

    context["offering"] = offering
    context["place_chart"] = plot_figure(
        figures.courses_confirmed_matched_lead_follow_free(offering)
    )
    context["time_chart"] = offering_time_chart_dict(offering)
    return render(request, template_name, context)


@login_required
def user_courses(request: HttpRequest) -> HttpResponse:
    template_name = "user/user_courses.html"
    user_id = request.user.id
    user: User = (
        User.objects.filter(id=user_id)
        .prefetch_related(
            "profile",
            "teaching_courses__course__lesson_occurrences",
            "profile__user__teaching_courses__course__lesson_occurrences",
        )
        .get()
    )
    profile = (
        UserProfile.objects.filter(user_id=user_id)
        .prefetch_related(
            "user__teaching_courses__course__lesson_occurrences",
            "user__lesson_occurrences__course__lesson_occurrences",
            "user__teaching_courses__course__survey_instances__survey",
            "user__lesson_occurrences__course__survey_instances__survey",
        )
        .get()
    )
    subscriptions = (
        user.subscriptions.prefetch_related(
            "course__lesson_occurrences",
            "course__irregular_lessons__lesson_details__room__cancellations",
            "course__regular_lessons__exceptions__lesson_details__room__cancellations",
            "course__room__cancellations",
            "course__type",
            "price_reductions",
            "course__period__cancellations",
            "course__offering__period__cancellations",
            "rejections",
            "partner__profile",
        )
        .order_by("-date")
        .all()
    )
    context = {
        "user": user,
        "profile": profile,
        "subscriptions": subscriptions,
        "token": _user_specific_token(user),
        "payment_account": settings.PAYMENT_ACCOUNT["default"],
    }
    return render(request, template_name, context)


def _user_specific_token(user: User) -> str:
    # without needing to extend the user, we can use its joined date (& time!),
    # salt it with the secret key, and we should have an acceptable (-> hardly guessable) hash
    str_to_hash = "{}-{}-{}".format(
        user.date_joined, os.environ.get("SECRET_KEY"), user.username
    )
    return hashlib.sha256(str_to_hash.encode()).hexdigest()


def user_ical(request: HttpRequest, user_id: int) -> HttpResponse:
    user = get_object_or_404(User, pk=user_id)

    security_token = request.GET.get("token", "")
    if security_token != _user_specific_token(user):
        raise PermissionDenied()
    
    cache_key = f"user_ical_{user_id}"
    response = cache.get(cache_key)
    if response:
        return response

    cal = Calendar()
    cal.add("version", "2.0")
    cal.add("prodid", f"-//Tanzquotient calendar for {user.get_full_name()}//mxm.dk//")
    cal.add("name", f"Tanzquotient - {user.get_full_name()} courses")
    cal.add("refresh-interval", vDuration(timedelta(hours=12)))
    prefetch = [
        "course__translations",
        "course__type__translations",
        "course__room",
        "course__lesson_occurrences",
        "course__teaching__teacher__profile",
    ]
    subscriptions = Subscribe.objects.filter(user=user).prefetch_related(*prefetch)
    courses_as_student = {
        subscription.course: subscription
        for subscription in subscriptions
        if subscription.state not in SubscribeState.REJECTED_STATES
    }
    teachings = user.teaching_courses.prefetch_related(*prefetch).all()
    courses_as_teacher = [t.course for t in teachings if not t.course.cancelled]
    courses = courses_as_student.keys() | set(courses_as_teacher)
    for course in courses:
        subscription = courses_as_student.get(course, None)
        for occurrence in course.lesson_occurrences.all():
            cal.add_component(
                _lesson_to_ical_event(course, occurrence, request, subscription)
            )

    response = HttpResponse(cal.to_ical(), content_type="text/calendar")
    cache.set(cache_key, response, 60 * 60 * 24)
    return response


@login_required
def user_profile(request: HttpRequest) -> HttpResponse:
    template_name = "user/profile.html"
    context = {"user": request.user}
    return render(request, template_name, context)


@method_decorator(login_required, name="dispatch")
class ProfileView(FormView):
    template_name = "courses/auth/profile.html"
    form_class = UserEditForm

    success_url = reverse_lazy("edit_profile")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_initial(self) -> dict:
        initial = create_initial_from_user(self.request.user)
        return initial

    def get_context_data(self, **kwargs) -> dict:
        # Call the base implementation first to get a context
        context = super(ProfileView, self).get_context_data(**kwargs)

        user = self.request.user
        context["is_teacher"] = user.profile.is_teacher()
        context["is_board_member"] = user.profile.is_board_member()
        context["is_profile_complete"] = user.profile.is_complete()
        context["profile_missing_values"] = user.profile.missing_values()
        return context

    def form_valid(self, form) -> HttpResponse:
        services.update_user(self.request.user, form.cleaned_data)
        return super(ProfileView, self).form_valid(form)


@login_required
def change_password(request: HttpRequest) -> HttpResponse:
    success = True
    initial = True
    if request.method == "POST":
        initial = False
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
        else:
            success = False
    else:
        form = PasswordChangeForm(request.user)

    return render(
        request,
        "account/change_password.html",
        {
            "form": form,
            "success": success,
            "initial": initial,
        },
    )


@staff_member_required
def export_summary(request: HttpRequest) -> HttpResponse:
    from courses import services

    return services.export_summary("csv")


@staff_member_required
def export_summary_excel(request: HttpRequest) -> HttpResponse:
    from courses import services

    return services.export_summary("xlsx")


@staff_member_required
def export_offering_summary(request: HttpRequest, offering_id: int) -> HttpResponse:
    from courses import services

    return services.export_summary(
        "csv", [Offering.objects.filter(pk=offering_id).first()]
    )


@staff_member_required
def export_offering_summary_excel(
    request: HttpRequest, offering_id: int
) -> HttpResponse:
    from courses import services

    return services.export_summary(
        "xlsx", [Offering.objects.filter(pk=offering_id).first()]
    )


@login_required
def cancel_subscription_from_waiting_list(
    request: HttpRequest, subscription_id: int
) -> HttpResponse:
    from courses.services import reject_subscriptions

    subscribe: Subscribe = get_object_or_404(
        Subscribe, id=subscription_id, user=request.user
    )
    assert subscribe.state == SubscribeState.WAITING_LIST

    subscriptions_to_reject = [subscribe]

    if subscribe.matching_state == MatchingState.COUPLE:
        partner_subscribe = subscribe.get_partner_subscription()
        assert partner_subscribe.state == SubscribeState.WAITING_LIST
        subscriptions_to_reject.append(partner_subscribe)

    reject_subscriptions(
        subscriptions=subscriptions_to_reject,
        reason=RejectionReason.USER_CANCELLED,
        send_email=True,
    )

    return render(
        request,
        "courses/subscription_cancellation_confirmation.html",
        {
            "course": subscribe.course,
            "couple": len(subscriptions_to_reject) > 1,
        },
    )
