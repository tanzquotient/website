from collections import Counter
from typing import Optional, Iterable

from django.utils.translation import gettext_lazy as _

from courses.models import Offering, Course
from survey.models import Question, Answer
from survey.models.types import QuestionType
from utils.plots import bar_chart, pie_chart, plot_figure


def _plot_for_scale(question: Question, answer_set: Iterable[Answer]) -> str:
    answer_counts = Counter([answer.value for answer in answer_set])
    values = [answer_counts.get(str(v), 0) for v in range(1, 6)]
    labels = [
        f"{question.scale.low} - 1" if question.scale else "1",
        "2",
        "3",
        "4",
        f"{question.scale.up} - 5" if question.scale else "5",
    ]
    return plot_figure(bar_chart(values, labels))


def _get_data_from_choices(question: Question, answers: list[str]):
    answer_counts = Counter(answers)
    choices = list(question.choice_set.all())
    values = [answer_counts[choice.value] for choice in choices]
    labels = [choice.label for choice in choices]
    other = len(answers) - sum(values)
    if other > 0:
        labels.append(str(_("Other")))
        values.append(other)
    return values, labels


def _plot_for_single_choice(question: Question, answer_set: Iterable[Answer]) -> str:
    answers = [answer.value for answer in answer_set if answer.value]
    values, labels = _get_data_from_choices(question, answers)
    return plot_figure(pie_chart(values, labels))


def _plot_for_multiple_choice(question: Question, answer_set: Iterable[Answer]) -> str:
    answers = []
    for answer in answer_set:
        for value in answer.value.split(';'):
            if value:
                answers.append(value)

    values, labels = _get_data_from_choices(question, answers)

    return plot_figure(bar_chart(values, labels))


def get_plot_for_question(question: Question, selected_offering: Offering, selected_course: Course) -> Optional[str]:
    answer_set = question.answers
    if selected_offering:
        answer_set = answer_set.filter(survey_instance__course__offering=selected_offering)
    if selected_course:
        answer_set = answer_set.filter(survey_instance__course=selected_course)
    answer_set = answer_set.all()

    if question.type == QuestionType.SCALE:
        return _plot_for_scale(question, answer_set)
    if question.type in [QuestionType.SINGLE_CHOICE, QuestionType.SINGLE_CHOICE_WITH_FREE_FORM]:
        return _plot_for_single_choice(question, answer_set)
    if question.type in [QuestionType.MULTIPLE_CHOICE, QuestionType.MULTIPLE_CHOICE_WITH_FREE_FORM]:
        return _plot_for_multiple_choice(question, answer_set)

    return None
