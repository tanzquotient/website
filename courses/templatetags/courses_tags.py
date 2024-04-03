from django import template
from django.db.models import QuerySet, Q

from courses.models import Weekday, OfferingType, Course
from courses.services import get_offerings_by_year
from survey.models import SurveyInstance, Answer
from survey.models.types import QuestionType
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import HttpRequest

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
            expire_date_query, user=user, is_completed=False
        ).count()
        > 0
    )


@register.simple_tag
def get_open_surveys(user: User) -> tuple[SurveyInstance]:

    expire_date_query = Q(url_expire_date__gte=timezone.now()) | Q(url_expire_date=None)

    return tuple(
        SurveyInstance.objects.filter(
            expire_date_query, user=user, is_completed=False
        ).all()
    )
