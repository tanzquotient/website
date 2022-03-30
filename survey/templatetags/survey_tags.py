from django import template

from courses.models import Offering, Course
from ..models import Question
from ..utils import get_plot_for_question, get_free_form_answers_for_question

register = template.Library()


@register.inclusion_tag(filename='survey/components/question_result.html')
def survey_question(question: Question, selected_offering: Offering, selected_course: Course):
    return dict(
        question=question,
        plot=get_plot_for_question(question, selected_offering, selected_course),
        free_form_answers=get_free_form_answers_for_question(question, selected_offering, selected_course),
    )
