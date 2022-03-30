from collections import Counter
from typing import Iterable

from courses.models import Offering, Course
from survey.models import Question, Answer
from survey.models.types import QuestionType


def _free_form_single_choice(question: Question, answer_set: Iterable[Answer]) -> list[str]:
    answers = [answer.value for answer in answer_set if answer.value]
    choices = {choice.value for choice in question.choice_set.all()}
    return [answer for answer in answers if answer not in choices]


def _free_form_multiple_choice(question: Question, answer_set: Iterable[Answer]) -> list[str]:
    answers = []
    for answer in answer_set:
        for value in answer.value.split(';'):
            if value:
                answers.append(value)

    choices = {choice.value for choice in question.choice_set.all()}
    return [answer for answer in answers if answer not in choices]


def get_free_form_answers_for_question(question: Question, selected_offering: Offering, selected_course: Course) \
        -> list[str]:

    answer_set = question.answers
    if selected_offering:
        answer_set = answer_set.filter(survey_instance__course__offering=selected_offering)
    if selected_course:
        answer_set = answer_set.filter(survey_instance__course=selected_course)
    answer_set = answer_set.all()

    values = []

    if question.type == QuestionType.SINGLE_CHOICE_WITH_FREE_FORM:
        values = _free_form_single_choice(question, answer_set)
    elif question.type == QuestionType.MULTIPLE_CHOICE_WITH_FREE_FORM:
        values = _free_form_multiple_choice(question, answer_set)
    elif question.type == QuestionType.FREE_FORM:
        values = [answer.value for answer in answer_set if answer.value]

    counts = Counter(values)
    value_count_tuples = [(value, count) for value, count in counts.items()]
    value_count_tuples.sort(key=lambda value_count: value_count[1], reverse=True)
    result = [f"{count}x: {value}" if count > 1 else value for value, count in value_count_tuples]

    return result
