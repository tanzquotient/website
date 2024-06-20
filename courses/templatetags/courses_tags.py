from django import template
from django.contrib.auth.models import User
from django.db.models import QuerySet, Q
from django.http import HttpRequest
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from courses.models import (
    Weekday,
    OfferingType,
    Course,
    Subscribe,
    SubscribeState, LeadFollow,
    LessonOccurrence,
    MatchingState,
)
from courses.services import get_offerings_by_year
from survey.models import SurveyInstance, Answer
from survey.models.types import QuestionType

register = template.Library()


@register.filter
def trans_weekday(key: str) -> str:
    return Weekday.WEEKDAYS_TRANSLATIONS[key]


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
        course_reviews=course_reviews_for_queryset(course_answers),
        teachers_reviews=course_reviews_for_queryset(teachers_answers),
        user=user,
        request=request,
    )


def course_reviews_for_queryset(answers: QuerySet[Answer]) -> list:
    text_answers = (
        answers.filter(
            question__type=QuestionType.FREE_FORM,
            hide_from_public_reviews=False,
            question__public_review=True,
        )
        .prefetch_related(
            "survey_instance",
            "question",
            "survey_instance__course__room",
            "survey_instance__course__type",
            "survey_instance__course__teaching__teacher",
        )
        .order_by("-survey_instance__last_update")
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

    return (
        SurveyInstance.objects.filter(
            expire_date_query, course_query, user=user
        ).count()
        > 0
    )


@register.simple_tag
def user_has_reviewed(
    course: Course, user: User, include_same_type: bool = True
) -> bool:
    course_query = (
        Q(course__type=course.type) if include_same_type else Q(course=course)
    )

    return (
        SurveyInstance.objects.filter(
            course_query, user=user, is_completed=False
        ).count()
        == 0
    )


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

    return (
        SurveyInstance.objects.filter(
            expire_date_query, user=user, is_completed=False, course__isnull=False
        ).count()
        > 0
    )


@register.simple_tag
def get_open_surveys(user: User) -> tuple[SurveyInstance]:
    expire_date_query = Q(url_expire_date__gte=timezone.now()) | Q(url_expire_date=None)

    return tuple(
        SurveyInstance.objects.filter(
            expire_date_query, user=user, is_completed=False, course__isnull=False
        ).all()
    )


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
    print(course.subscriptions.get(user=user))
    return course.subscriptions.get(user=user)


@register.filter(name="get_waiting_list_composition")
def get_waiting_list_composition(course: Course) -> list|None:
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

    return composition
