from django import template

from courses.services import get_offerings_by_year
from courses.models import *
from survey.models import Question, Answer
from survey.models.types import QuestionType

register = template.Library()


@register.filter
def trans_weekday(key: str) -> str:
    return Weekday.WEEKDAYS_TRANSLATIONS[key]


@register.inclusion_tag(filename='courses/snippets/offerings_list.html')
def offerings_list(detail_url: str, only_public: bool = True) -> dict:
    offering_types = [OfferingType.REGULAR, OfferingType.IRREGULAR]
    return dict(
        detail_url=detail_url,
        offerings=get_offerings_by_year(offering_types, only_public),
        offering_types=offering_types,
    )


@register.inclusion_tag(filename='courses/snippets/course_reviews.html')
def course_reviews(course: Course) -> dict:
    answers = Answer.objects.filter(hide_from_public_reviews=False,
                                    question__public_review=True,
                                    survey_instance__course__type=course.type).prefetch_related(
        'survey_instance', 'question').distinct()

    text_answers = answers.filter(question__type=QuestionType.FREE_FORM).order_by('-survey_instance__last_update')

    text_reviews = [dict(text=answer.value, date=answer.survey_instance.last_update) for answer in text_answers]
    show_reviews = len(text_reviews) > 0

    return dict(show_reviews=show_reviews, text_reviews=text_reviews)
