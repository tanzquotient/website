#!/usr/bin/python
# -*- coding: UTF-8 -*-
from django.conf.urls import patterns, url, include

from .api import *

urlpatterns = patterns('',
                       url(r'^survey/(?P<pk>\d+)/$', SurveyDetail.as_view(), name='survey-detail'),
                       url(r'^answer/(?P<pk>\d+)/$', SurveyAnswer.as_view(), name='answer-detail'),
                       )
