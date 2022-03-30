from django.urls import path

import survey.views.survey_view
from survey import views

app_name = 'survey'
urlpatterns = [
    path('<int:survey_id>/results/', views.survey_results, name='survey_results'),
    path('<int:survey_id>/', survey.views.survey_view, name='survey'),
    path('<int:survey_id>/<url_key>/', survey.views.survey_view, name='survey_with_key'),
]
