from django.conf.urls import url
from .ical import EventFeed

app_name = 'events'
urlpatterns = [
    url(r'^calendar.ics', EventFeed(), name='ical'),
]
