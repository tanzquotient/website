from django.urls import path

from survey import views

app_name = "survey"
urlpatterns = [
    path("", views.overview, name="overview"),
    path("teacher/", views.overview_as_teacher, name="overview_as_teacher"),
    path("changed_answers/", views.changed_answers, name="changed_answers"),
    path("<int:survey_id>/", views.survey_view, name="survey"),
    path("<int:survey_id>/results/", views.results, name="results"),
    path("<int:survey_id>/download/", views.download, name="download"),
    path("<int:survey_id>/<url_key>/", views.survey_view, name="survey_with_key"),
]
