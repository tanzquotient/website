from parler_rest.serializers import TranslatableModelSerializer
from rest_framework import serializers

from survey.models import *


class ChoiceSerializer(TranslatableModelSerializer):
    class Meta:
        model = Choice
        fields = ("id", "label")


class QuestionSerializer(TranslatableModelSerializer):
    choice_set = ChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = ("id", "name", "text", "note", "type", "choice_set")


class QuestionGroupSerializer(TranslatableModelSerializer):
    question_set = QuestionSerializer(many=True)

    class Meta:
        model = QuestionGroup
        fields = ("id", "name", "intro_text", "question_set")


class SurveySerializer(TranslatableModelSerializer):
    questiongroup_set = QuestionGroupSerializer(many=True)

    class Meta:
        model = Survey
        fields = ("id", "intro_text", "questiongroup_set", "language_code")


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ("id", "value")
