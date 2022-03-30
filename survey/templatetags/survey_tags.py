from django import template

from ..models import Question
from ..utils import get_plot_for_question, get_free_form_answers_for_question

register = template.Library()


@register.inclusion_tag(filename='survey/components/question_result.html')
def survey_question(question: Question):
    return dict(
        question=question,
        plot=get_plot_for_question(question),
        free_form_answers=get_free_form_answers_for_question(question),
    )
