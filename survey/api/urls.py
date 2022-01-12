from django.urls import path

from .api import *

app_name = 'survey_api'
urlpatterns = [
    path('survey/<int:pk>/', SurveyDetail.as_view(), name='survey-detail'),
    path('answer/<int:pk>/', SurveyAnswer.as_view(), name='answer-detail'),
]
