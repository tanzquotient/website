from django.urls import path

from . import views

app_name = "url_shortener"

urlpatterns = [
    path("", views.redirect_to_destination, name="redirect"),
]
