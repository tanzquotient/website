import datetime
import os

from django.urls import reverse
from django.utils.html import strip_tags
from django_ical.views import ICalFeed

from .models import Event


class EventFeed(ICalFeed):
    # A unique id for this calendar. For details see: http://www.kanzaki.com/docs/ical/prodid.html
    product_id = '-//TQ Website calendar v1.1'

    def items(self):
        return Event.objects.all()

    def item_title(self, item):
        return item.safe_translation_getter("name", any_language=True) or "Untitled"

    def item_description(self, item):
        description = item.name
        description += os.linesep
        description += item.safe_translation_getter("description", any_language=True) or ""

        price_string = item.format_prices()
        if price_string:
            description += os.linesep
            description += price_string

        # add link (depending on item type) also to description since some calendar programs do not display link field
        description += os.linesep
        description += self.item_link(item)

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
        return reverse('courses:course_overview')

    # must be unique in order to display all events correctly in most calendar programs
    def item_guid(self, item):
        domain = 'tanzquotient'
        namespace = 'event'
        guid = '{0}_{1}_{2}'.format(domain, namespace, item.id)
        return guid
