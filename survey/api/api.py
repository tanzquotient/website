from rest_framework import generics, permissions
from rest_framework.viewsets import ReadOnlyModelViewSet

from .serializers import *


class SurveyDetail(generics.RetrieveAPIView):
    model = Survey
    serializer_class = SurveySerializer
    queryset = Survey.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]


class SurveyAnswer(ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = AnswerSerializer
    queryset = Answer.objects.all()
