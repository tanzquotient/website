from collections import Counter
from typing import Optional

from plotly.graph_objs import Figure
from plotly.offline import plot
from django.utils.translation import gettext_lazy as _


from utils.plots import bar_chart, pie_chart
from survey.models import Question
from survey.models.types import QuestionType


def _plot(figure: Figure) -> str:
    config = dict(
        displayModeBar=False,
    )
    return plot(figure, output_type='div', include_plotlyjs=False, config=config)


def _plot_for_scale(question: Question) -> str:
    answer_counts = Counter([answer.value for answer in question.answers.all()])
    values = [answer_counts.get(str(v), 0) for v in range(1, 6)]
    labels = [
        f"{question.scale.low} - 1" if question.scale else "1",
        "2",
        "3",
        "4",
        f"{question.scale.up} - 5" if question.scale else "5",
    ]
    return _plot(bar_chart(values, labels))


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


def _plot_for_single_choice(question: Question) -> str:
    answers = [answer.value for answer in question.answers.all() if answer.value]
    values, labels = _get_data_from_choices(question, answers)
    return _plot(pie_chart(values, labels))


def _plot_for_multiple_choice(question: Question) -> str:
    answers = []
    for answer in question.answers.all():
        for value in answer.value.split(';'):
            if value:
                answers.append(value)

    values, labels = _get_data_from_choices(question, answers)

    return _plot(bar_chart(values, labels))


def get_plot_for_question(question: Question) -> Optional[str]:
    if question.type == QuestionType.SCALE:
        return _plot_for_scale(question)
    if question.type in [QuestionType.SINGLE_CHOICE, QuestionType.SINGLE_CHOICE_WITH_FREE_FORM]:
        return _plot_for_single_choice(question)
    if question.type in [QuestionType.MULTIPLE_CHOICE, QuestionType.MULTIPLE_CHOICE_WITH_FREE_FORM]:
        return _plot_for_multiple_choice(question)

    return None
