from __future__ import annotations

from typing import Optional

from django.db.models import Model, TextField, ForeignKey, CASCADE, PROTECT
from django.shortcuts import get_object_or_404
from . import Question, Choice


class Answer(Model):
    survey_instance = ForeignKey('SurveyInstance', related_name='answers', blank=False, null=True, on_delete=CASCADE)
    question = ForeignKey('Question', related_name='answers', blank=False, null=True, on_delete=PROTECT)
    choice = ForeignKey('Choice', blank=True, null=True, on_delete=PROTECT)
    text = TextField(blank=True, null=True)

    @classmethod
    def create(cls, survey_inst, question, choice, choice_input=None) -> Answer:
        """Creates Answer parsing input and deciding which fields to set, depending on question type"""
        if question.type in [Question.Type.SINGLE_CHOICE, Question.Type.MULTIPLE_CHOICE]:
            # here we expect choice to be a valid id
            choice = get_object_or_404(Choice, pk=choice)
            choice.set_current_language('en')
            return cls(survey_instance=survey_inst, question=question, choice=choice, text=choice.label)
        if question.type in [Question.Type.SINGLE_CHOICE_WITH_FREE_FORM, Question.Type.MULTIPLE_CHOICE_WITH_FREE_FORM]:
            if choice == 'freeform':
                return cls(survey_instance=survey_inst, question=question, text=choice_input)
            else:
                choice = get_object_or_404(Choice, pk=choice)
                choice.set_current_language('en')
                return cls(survey_instance=survey_inst, question=question, choice=choice, text=choice.label)
        if question.type == Question.Type.SCALE:
            return cls(survey_instance=survey_inst, question=question, text=choice_input)
        if question.type == Question.Type.FREE_FORM:
            if choice == 'default':
                return cls(survey_instance=survey_inst, question=question, text=choice_input)
            else:
                choice = get_object_or_404(Choice, pk=choice)
                return cls(survey_instance=survey_inst, question=question, choice=choice, text=choice_input)

    def value(self) -> Optional[str]:
        if self.text:
            return self.text
        if self.choice:
            return self.choice.get_question_name()
        return None

    def __str__(self) -> str:
        return self.value() or "<not answered>"
