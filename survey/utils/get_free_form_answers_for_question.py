from collections import Counter
from typing import Iterable

from courses.models import Offering, Course
from survey.models import Question, Answer
from survey.models.types import QuestionType


def _free_form_single_choice(
    question: Question, answer_set: Iterable[Answer]
) -> list[Answer]:
    answers = [answer for answer in answer_set if answer.value]
    choices = {choice.value for choice in question.choice_set.all()}
    return [answer for answer in answers if answer.value not in choices]


def _free_form_multiple_choice(
    question: Question, answer_set: Iterable[Answer]
) -> list[Answer]:
    choices = {choice.value for choice in question.choice_set.all()}
    answers = []
    for answer in answer_set:
        for value in answer.value.split(";"):
            if value and value not in choices:
                answers.append(
                    Answer(
                        pk=answer.pk,
                        value=value,
                        question=answer.question,
                        hide_from_public_reviews=answer.hide_from_public_reviews,
                        survey_instance=answer.survey_instance,
                    )
                )

    return answers


def get_free_form_answers_for_question(
    question: Question, selected_offering: Offering, selected_course: Course
) -> list[str]:
    answer_set = question.answers
    if selected_offering:
        answer_set = answer_set.filter(
            survey_instance__course__offering=selected_offering
        )
    if selected_course:
        answer_set = answer_set.filter(survey_instance__course=selected_course)
    answer_set = answer_set.all()

    values = []

    if question.type == QuestionType.SINGLE_CHOICE_WITH_FREE_FORM:
        values = _free_form_single_choice(question, answer_set)
    elif question.type == QuestionType.MULTIPLE_CHOICE_WITH_FREE_FORM:
        values = _free_form_multiple_choice(question, answer_set)
    elif question.type == QuestionType.FREE_FORM:
        values = [answer for answer in answer_set if answer.value]

    return sorted(
        values, key=lambda answer: answer.survey_instance.last_update, reverse=True
    )
