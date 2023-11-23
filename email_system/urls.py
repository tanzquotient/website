from django.urls import path

from email_system import views
from email_system.apps import EmailSystemConfig

app_name = EmailSystemConfig.name
urlpatterns = [
    path(
        "unsubscribe/<str:context>/<int:user_id>/<slug:code>/",
        views.unsubscribe,
        name="unsubscribe",
    ),
]
