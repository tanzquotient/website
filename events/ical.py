import os
import datetime
import hashlib
from django.utils.html import strip_tags
from django_ical.views import ICalFeed
from .models import Event
from django.core.urlresolvers import reverse


class EventFeed(ICalFeed):
    # A unique id for this calendar. For details see: http://www.kanzaki.com/docs/ical/prodid.html
    product_id = '-//TQ Website calendar v1.0'

    def items(self):
        return Event.objects.all()

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        description = item.name
        description += os.linesep
        description += item.description

        if not item.price_special:
            if not (item.price_with_legi is None):
                description += os.linesep
                description += 'Price with Legi: {}'.format(item.price_with_legi)
            if not (item.price_without_legi is None):
                description += os.linesep
                description += 'Price without Legi: {}'.format(item.price_without_legi)
        else:
            description += item.price_special
        description = strip_tags(description)

        description += os.linesep
        description += 'https://tanzquotient.org/en/events/'

        return description

    def item_start_datetime(self, item):
        date = item.date
        if item.time_from is None:
            # no start time is available
            return date
        return datetime.datetime.combine(date, item.time_from)

    def item_end_datetime(self, item):
        date = item.date
        if item.time_to is None:
            # no end time is available
            return date
        return datetime.datetime.combine(date, item.time_to)

    def item_location(self, item):
        return item.room

    def item_link(self, item):
        # remember to change this value when the calendar url changes
        return 'https://tanzquotient.org/en/events/'

    # must be unique in order to display all events correctly in most calendar programs
    def item_guid(self, item):
        # for details about the construction, see http://www.kanzaki.com/docs/ical/uid.html
        current_datetime = datetime.datetime.utcnow()
        # format current datetime: YYYYMMDD'T'HHmmSS
        current_datetime = current_datetime.strftime('%Y%m%dT%H%M%S')
        pid = os.getpid()
        domain = 'tanzquotient.org'
        guid = '{0}-{1}-{2}@{3}'.format(current_datetime, pid, item.id, domain)
        return guid
