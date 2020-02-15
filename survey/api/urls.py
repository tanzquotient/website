from django.conf.urls import url

from .api import *

app_name = 'survey_api'
urlpatterns = [
    url(r'^survey/(?P<pk>\d+)/$', SurveyDetail.as_view(), name='survey-detail'),
    url(r'^answer/(?P<pk>\d+)/$', SurveyAnswer.as_view(), name='answer-detail'),
]
