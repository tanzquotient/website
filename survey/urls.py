from django.conf.urls import patterns, url, include

from survey import views

urlpatterns = patterns('',
                       url(r'^$', views.survey_invitation, name='survey_invitation'),
                       )