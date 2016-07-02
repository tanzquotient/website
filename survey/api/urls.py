#!/usr/bin/python
# -*- coding: UTF-8 -*-
from django.conf.urls import url, include

from .api import *

urlpatterns = [
    url(r'^survey/(?P<pk>\d+)/$', SurveyDetail.as_view(), name='survey-detail'),
    url(r'^answer/(?P<pk>\d+)/$', SurveyAnswer.as_view(), name='answer-detail'),
]
