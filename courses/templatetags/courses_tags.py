from django import template
from django.db.models import QuerySet

from courses.models import Weekday, OfferingType, Course
from courses.services import get_offerings_by_year
from survey.models import Answer
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
def course_reviews(course: Course) -> dict:
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
    )


def course_reviews_for_queryset(answers: QuerySet[Answer]) -> list:
    text_answers = (
        answers.filter(
            question__type=QuestionType.FREE_FORM,
            hide_from_public_reviews=False,
            question__public_review=True,
        )
        .prefetch_related("survey_instance", "question")
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
