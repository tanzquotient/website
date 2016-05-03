from django.conf.urls import patterns, url, include

from survey import views

urlpatterns = patterns('',
                       url(r'^$', views.survey_invitation, name='survey_invitation'),
                       url(r'^api/', include('survey.api.urls', namespace='api')),  # nested namespace 'api'
                       url(r'^(?P<survey_id>\d+)/$', views.survey_test, name='survey_test'),
                       )