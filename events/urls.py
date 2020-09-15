from django.conf.urls import url

from . import views
from .ical import EventFeed

app_name = 'events'
urlpatterns = [
    url(r'^calendar.ics', EventFeed(), name='ical'),
    url(r'^(?P<event_id>\d+)/detail/$', views.detail, name='detail'),
    url(r'^(?P<event_id>\d+)/reserve/$', views.register, name='register'),
    url(r'^(?P<event_id>\d+)/confirmation/$', views.registration_confirmation, name='registration_confirmation'),
]
