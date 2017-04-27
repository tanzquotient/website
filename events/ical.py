import os
import datetime
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

        return strip_tags(description)

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
        return reverse('events:ical')
