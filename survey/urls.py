from django.urls import path

from survey import views

app_name = 'survey'
urlpatterns = [
    path('<int:survey_id>/', views.survey_view, name='survey'),
    path('<int:survey_id>/<url_key>/', views.survey_view, name='survey_with_key'),
    # path('api/', include(survey.api.urls, namespace='survey_api')),  # nested namespace 'api'
]
