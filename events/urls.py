from django.conf.urls import url

from . import views
from .ical import EventFeed

app_name = 'events'
urlpatterns = [
    url(r'^calendar.ics', EventFeed(), name='ical'),
    url(r'^(?P<event_id>\d+)/detail/$', views.event_detail, name='event_detail'),
    url(r'^(?P<event_id>\d+)/reserve/$', views.event_reserve, name='event_reserve'),
]
