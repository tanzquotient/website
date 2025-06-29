import datetime as dt
from datetime import datetime, timedelta

import pytz
from django import template
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import QuerySet, Q, Count
from django.http import HttpRequest
from django.template.defaultfilters import date
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import courses.utils as utils
from courses.cms_plugins import MyNextLessonsPlugin
from courses.models import (
    Weekday,
    OfferingType,
    Course,
    Subscribe,
    SubscribeState,
    LeadFollow,
    MatchingState,
    RejectionReason,
    LessonOccurrence,
    Attendance,
)
from courses.services import get_offerings_by_year
from survey.models import SurveyInstance, Answer
from survey.models.types import QuestionType

register = template.Library()

TIME_ZONE = pytz.timezone(settings.TIME_ZONE)


@register.filter
def trans_weekday(key: str) -> str:
    return Weekday.WEEKDAYS_TRANSLATIONS[key]


@register.inclusion_tag(
    filename="courses/snippets/lesson_components/course_lessons.html"
)
def course_lessons_compact(course: Course) -> dict:
    lessons = list(course.lesson_occurrences.all())
    same_weekday = len({lesson.start.weekday() for lesson in lessons}) == 1
    same_start_time = len({l.start.astimezone(TIME_ZONE).time() for l in lessons}) == 1
    same_end_time = len({l.end.astimezone(TIME_ZONE).time() for l in lessons}) == 1
    is_regular = same_weekday and same_start_time and same_end_time
    if len(lessons) < 3 or not is_regular:
        return dict(lines=[format_duration(l.start, l.end) for l in lessons])

    last_lesson = lessons[-1]
    first_lesson = lessons[0]
    num_weeks = (last_lesson.start - first_lesson.start).days // 7
    lesson_dates = [lesson.start.date() for lesson in lessons]
    dates_in_period = [
        first_lesson.start.date() + timedelta(days=7 * i) for i in range(num_weeks + 1)
    ]
    cancellations = [d for d in dates_in_period if d not in lesson_dates]

    cancellation_lines = (
        [f"{_('Cancellations')}: {', '.join([format_date(c) for c in cancellations])}"]
        if cancellations
        else []
    )

    regular_lines = [
        f"{date(first_lesson.start.astimezone(TIME_ZONE), 'D, H:i')} - "
        f"{date(first_lesson.end.astimezone(TIME_ZONE), 'H:i')}, "
        f"{format_period(start=first_lesson.start.date(), end=last_lesson.end.date())}",
    ]

    if len(lessons) <= len(regular_lines) + len(cancellation_lines):
        return dict(lines=[format_duration(l.start, l.end) for l in lessons])

    return dict(lines=regular_lines + cancellation_lines)


@register.inclusion_tag(
    filename="courses/snippets/lesson_components/course_lessons.html"
)
def course_lessons_detailed(course: Course) -> dict:
    if len(course.rooms) < 2:
        return course_lessons_compact(course)

    lines = []
    lesson_occurrences: QuerySet[LessonOccurrence] = course.lesson_occurrences.all()
    for lesson in lesson_occurrences:
        lesson: LessonOccurrence
        lines += [
            f"{date(lesson.start.astimezone(TIME_ZONE), 'D, d. b, H:i')} - "
            f"{date(lesson.end.astimezone(TIME_ZONE), 'H:i')}, "
            f"{lesson.room.name}"
        ]

    return dict(lines=lines)


@register.inclusion_tag(filename="courses/plugins/next_lessons/index.html")
def my_next_lessons_plugin(request: HttpRequest) -> dict:
    context = MyNextLessonsPlugin.create_context(request.user)
    context["request"] = request
    return context


@register.simple_tag
def format_duration(start: datetime, end: datetime) -> str:
    start = start.astimezone(TIME_ZONE)
    end = end.astimezone(TIME_ZONE)
    date_now = datetime.now()
    current_year = date_now.year
    format_date_without_year = start.year == end.year and start.year == current_year
    date_format = "D, d. N" if format_date_without_year else "D, d. N Y"
    time_format = "H:i"
    date_time_format = f"{date_format}, {time_format}"
    if start.date() == end.date():
        return f"{date(start, date_format)}, {date(start, time_format)} - {date(end, time_format)}"

    return f"{date(start, date_time_format)} - {date(end, date_time_format)}"


@register.simple_tag
def format_period(start: dt.date, end: dt.date) -> str:
    today = dt.date.today()
    current_year = today.year
    format_date_without_year = start.year == end.year and start.year == current_year
    date_format = "d. N" if format_date_without_year else "d. N Y"
    return f"{date(start, date_format)} - {date(end, date_format)}"


@register.simple_tag
def format_date(value: dt.date) -> str:
    today = dt.date.today()
    current_year = today.year
    format_date_without_year = value.year == current_year
    date_format = "d. N" if format_date_without_year else "d. N Y"
    return date(value, date_format)


@register.inclusion_tag(filename="courses/snippets/offerings_list.html")
def offerings_list(detail_url: str, only_public: bool = True) -> dict:
    offering_types = [OfferingType.REGULAR, OfferingType.IRREGULAR]
    return dict(
        detail_url=detail_url,
        offerings=get_offerings_by_year(offering_types, only_public),
        offering_types=offering_types,
    )


@register.inclusion_tag(filename="courses/snippets/course_reviews.html")
def course_reviews(course: Course, user: User, request: HttpRequest) -> dict:
    course_answers = Answer.objects.filter(
        survey_instance__course__type=course.type,
    )

    course_teachers = course.get_teachers()
    teachers_answers = Answer.objects.exclude(
        survey_instance__course__type=course.type,
    ).filter(survey_instance__course__teaching__teacher__in=course_teachers)
    return dict(
        course=course,
        course_reviews=course_reviews_for_queryset(course_answers, course_teachers),
        teachers_reviews=course_reviews_for_queryset(teachers_answers, course_teachers),
        user=user,
        request=request,
    )


def course_reviews_for_queryset(
    answers: QuerySet[Answer], teachers: list[User]
) -> list:
    text_answers = (
        answers.filter(
            question__type=QuestionType.FREE_FORM,
            hide_from_public_reviews=False,
            question__public_review=True,
        )
        .annotate(
            matching_teachers=Count(
                "survey_instance__course__teaching",
                filter=Q(survey_instance__course__teaching__teacher__in=teachers),
            ),
        )
        .prefetch_related(
            "survey_instance",
            "question",
            "survey_instance__course__room",
            "survey_instance__course__type",
            "survey_instance__course__teaching__teacher",
        )
        .order_by("-matching_teachers", "-survey_instance__last_update")
        .distinct()
    )

    return [
        dict(
            text=answer.value,
            date=answer.survey_instance.last_update,
            course=answer.survey_instance.course,
        )
        for answer in text_answers
    ]


@register.simple_tag
def user_has_taken_course(
    course: Course, user: User, include_same_type: bool = True
) -> bool:
    course_query = (
        Q(course__type=course.type) if include_same_type else Q(course=course)
    )

    subscriptions = Subscribe.objects.filter(
        course_query,
        user=user,
        state__in=SubscribeState.ACCEPTED_STATES,
    ).all()

    for subscription in subscriptions:
        if subscription.course.is_over():
            return True

    return False


@register.simple_tag
def user_can_review(course: Course, user: User, include_same_type: bool = True) -> bool:
    course_query = (
        Q(course__type=course.type) if include_same_type else Q(course=course)
    )
    expire_date_query = Q(url_expire_date__gte=timezone.now()) | Q(url_expire_date=None)

    return SurveyInstance.objects.filter(
        expire_date_query, course_query, user=user
    ).exists()


@register.simple_tag
def user_has_reviewed(
    course: Course, user: User, include_same_type: bool = True
) -> bool:
    course_query = (
        Q(course__type=course.type) if include_same_type else Q(course=course)
    )

    return not SurveyInstance.objects.filter(
        course_query, user=user, is_completed=False
    ).exists()


@register.simple_tag
def get_link_to_course_evaluation(
    course: Course, user: User, include_same_type: bool = True
) -> str:
    expire_date_query = Q(url_expire_date__gte=timezone.now()) | Q(url_expire_date=None)

    survey_instance = SurveyInstance.objects.filter(
        expire_date_query, user=user, is_completed=False, course=course
    )

    if include_same_type and survey_instance.count() == 0:
        survey_instance = SurveyInstance.objects.filter(
            expire_date_query, user=user, is_completed=False, course__type=course.type
        )

    return survey_instance[0].create_full_url() if survey_instance.count() > 0 else "#"


@register.simple_tag
def has_open_surveys(user: User) -> bool:
    expire_date_query = Q(url_expire_date__gte=timezone.now()) | Q(url_expire_date=None)

    return SurveyInstance.objects.filter(
        expire_date_query, user=user, is_completed=False, course__isnull=False
    ).exists()


@register.simple_tag
def get_open_surveys(user: User) -> tuple[SurveyInstance]:
    expire_date_query = Q(url_expire_date__gte=timezone.now()) | Q(url_expire_date=None)

    return tuple(
        SurveyInstance.objects.filter(
            expire_date_query, user=user, is_completed=False, course__isnull=False
        ).all()
    )


@register.simple_tag
def role(user: User, lesson: LessonOccurrence) -> str:
    return utils.role(user.id, lesson)


@register.simple_tag
def has_assigned_role(user: User, course: Course) -> bool:
    return role(user, course) != LeadFollow.NO_PREFERENCE


@register.simple_tag
def attendance_state(user: User, lesson: LessonOccurrence) -> str:
    attendance = lesson.attendances.all()
    for attendance in attendance:
        if attendance.user_id == user.id:
            return attendance.state
    return Attendance.DEFAULT_STATE


@register.filter(name="is_over_since")
def is_over_since(course: Course, days: int) -> bool:
    return course.is_over_since(days=days)


@register.filter(name="missing_presence_data")
def missing_presence_data(course: Course) -> bool:
    return course.lesson_occurrences.filter(
        end__lte=timezone.localtime.now(), teachers=None
    ).exists()


@register.filter(name="get_waiting_list_length")
def get_waiting_list_length(course: Course, lead_follow: str = "no_preference") -> int:
    if lead_follow == "lead":
        lead_follow = LeadFollow.LEAD
    elif lead_follow == "follow":
        lead_follow = LeadFollow.FOLLOW
    else:
        lead_follow = LeadFollow.NO_PREFERENCE
    return course.get_waiting_list_length(lead_follow=lead_follow)


@register.filter(name="get_position_on_waiting_list")
def get_position_on_waiting_list(course: Course, user: User) -> int:
    # get user's subscription for course
    subscription: Subscribe = Subscribe.objects.get(course=course, user=user)
    return subscription.get_position_on_waiting_list()


@register.filter(name="user_can_subscribe")
def user_can_subscribe(course: Course, user: User) -> bool:
    return course.user_can_subscribe(user=user)


@register.filter(name="is_couple")
def is_couple(subscribe: Subscribe) -> bool:
    return subscribe.matching_state == MatchingState.COUPLE


@register.filter(name="get_user_subscription")
def get_user_subscription(course: Course, user: User) -> Subscribe:
    return course.subscriptions.get(user=user)


@register.filter(name="get_waiting_list_composition")
def get_waiting_list_composition(course: Course) -> list | None:
    waiting_list_subscriptions: list[Subscribe] = course.subscriptions.waiting_list()
    if not waiting_list_subscriptions.exists():
        return None

    composition = []

    # couples
    n_couples = (
        waiting_list_subscriptions.filter(matching_state=MatchingState.COUPLE).count()
        // 2
    )
    composition.append(
        _("One couple")
        if n_couples == 1
        else f"{n_couples} {_('couples')}" if n_couples > 0 else None
    )

    # individuals
    for lead_follow, text in [
        (
            LeadFollow.LEAD,
            lambda n: (
                _("One individual leader")
                if n == 1
                else f"{n} {_('individual leaders')}" if n > 0 else None
            ),
        ),
        (
            LeadFollow.FOLLOW,
            lambda n: (
                _("One individual follower")
                if n == 1
                else f"{n} {_('individual followers')}" if n > 0 else None
            ),
        ),
        (
            LeadFollow.NO_PREFERENCE,
            lambda n: (
                _("One person with no lead or follow preference")
                if n == 1
                else (
                    f"{n} {_('people with no lead or follow preference')}"
                    if n > 0
                    else None
                )
            ),
        ),
    ]:
        composition.append(
            text(
                waiting_list_subscriptions.filter(lead_follow=lead_follow)
                .exclude(matching_state=MatchingState.COUPLE)
                .count()
            )
        )

    return [text for text in composition if text is not None]


@register.filter(name="is_user_eligible_for_early_signup")
def is_user_eligible_for_early_signup(course: Course, user: User):
    return course.is_user_eligible_for_early_signup(user)


@register.filter(name="rejection_reason")
def rejection_reason(subscription: Subscribe) -> str:
    reasons = [r.reason for r in subscription.rejections.all()]
    return reasons[0] if len(reasons) > 0 else RejectionReason.UNKNOWN


@register.filter(name="rejection_reason_text")
def rejection_reason_text(reason: RejectionReason) -> str:
    if reason == RejectionReason.USER_CANCELLED:
        return _("You cancelled")
    if reason == RejectionReason.COURSE_CANCELLED:
        return _("Course cancelled")
    return _("Rejected")


@register.filter(name="rejection_reason_info")
def rejection_reason_info(reason: RejectionReason) -> str:
    if reason == RejectionReason.USER_CANCELLED:
        return _("You deregistered from this course")
    if reason == RejectionReason.COURSE_CANCELLED:
        return _("This course could unfortunately not take place.")
    return _("Rejected subscription info")
