from django.conf.urls import url
from .ical import EventFeed

urlpatterns = [
    url(r'^calendar.ics', EventFeed(), name='ical'),
]
