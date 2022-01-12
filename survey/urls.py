from django.conf.urls import include
from django.urls import path

import survey.api.urls
from survey import views

app_name = 'survey'
urlpatterns = [
    path('', views.survey_invitation, name='survey_invitation'),
    path('api/', include(survey.api.urls, namespace='survey_api')),  # nested namespace 'api'
    path('<int:survey_id>/', views.survey_test, name='survey_test'),
    path('done', views.survey_done, name='survey_done'),
    path('error', views.survey_error, name='survey_error'),
]
