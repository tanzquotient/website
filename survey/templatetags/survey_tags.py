from django import template
from django.contrib.auth.models import User
from reversion.models import Version

from courses.models import Offering, Course
from ..models import Question, Survey, Answer
from ..utils import get_plot_for_question, get_free_form_answers_for_question

register = template.Library()


@register.inclusion_tag(filename='survey/components/question_result.html')
def survey_question(question: Question, selected_offering: Offering, selected_course: Course, user: User):
    return dict(
        user=user,
        question=question,
        plot=get_plot_for_question(question, selected_offering, selected_course),
        free_form_answers=get_free_form_answers_for_question(question, selected_offering, selected_course),
    )


@register.inclusion_tag(filename='survey/components/question_result_free_form_answer.html')
def free_form_answer(answer: Answer, user: User):
    return dict(
        user=user,
        answer=answer
    )


@register.inclusion_tag(filename='survey/components/survey_card.html')
def survey_card(survey: Survey) -> dict:
    return dict(
        survey=survey,
        offerings=Offering.objects.filter(course__survey_instances__survey=survey).distinct().order_by('name').all(),
        questions=Question.objects.filter(question_group__survey=survey),
        answers_count=survey.survey_instances.filter(is_completed=True).count(),
    )
