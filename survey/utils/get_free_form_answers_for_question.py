from collections import Counter
from typing import Optional

from plotly.graph_objs import Figure
from plotly.offline import plot
from django.utils.translation import gettext_lazy as _


from utils.plots import bar_chart, pie_chart
from survey.models import Question
from survey.models.types import QuestionType


def _free_form_single_choice(question: Question) -> list[str]:
    answers = [answer.value for answer in question.answers.all() if answer.value]
    choices = {choice.value for choice in question.choice_set.all()}
    return [answer for answer in answers if answer not in choices]


def _free_form_multiple_choice(question: Question) -> list[str]:
    answers = []
    for answer in question.answers.all():
        for value in answer.value.split(';'):
            if value:
                answers.append(value)

    choices = {choice.value for choice in question.choice_set.all()}
    return [answer for answer in answers if answer not in choices]


def get_free_form_answers_for_question(question: Question) -> list[str]:
    values = []

    if question.type == QuestionType.SINGLE_CHOICE_WITH_FREE_FORM:
        values = _free_form_single_choice(question)
    elif question.type == QuestionType.MULTIPLE_CHOICE_WITH_FREE_FORM:
        values = _free_form_multiple_choice(question)
    elif question.type == QuestionType.FREE_FORM:
        values = [answer.value for answer in question.answers.all() if answer.value]

    counts = Counter(values)
    value_count_tuples = [(value, count) for value, count in counts.items()]
    value_count_tuples.sort(key=lambda value_count: value_count[1], reverse=True)
    result = [f"{count}x: {value}" if count > 1 else value for value, count in value_count_tuples]

    return result
