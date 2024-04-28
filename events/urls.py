from django.urls import path

from . import views
from .ical import EventFeed

app_name = "events"

urlpatterns = [
    path("calendar.ics", EventFeed(), name="ical"),
    path("<int:event_id>/detail/", views.detail, name="detail"),
    path("<int:event_id>/register/", views.register, name="register"),
    path("<int:event_id>/unregister/", views.unregister, name="unregister"),
    path(
        "<int:event_id>/confirmation/",
        views.registration_confirmation,
        name="registration_confirmation",
    ),
    path(
        "<int:event_id>/unregistered/",
        views.registration_removed,
        name="registration_removed",
    ),
    path(
        "categories/<int:category_id>/detail/",
        views.category_detail,
        name="category_detail",
    ),
    path("archive/", views.archive, name="archive_thisyear"),
    path("archive/<int:year>", views.archive, name="archive"),
]
