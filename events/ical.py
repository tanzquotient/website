import os
import datetime
from django.utils.html import strip_tags
from django_ical.views import ICalFeed
from courses.models import IrregularLesson, Offering
from .models import Event


class EventFeed(ICalFeed):
    # A unique id for this calendar. For details see: http://www.kanzaki.com/docs/ical/prodid.html
    product_id = '-//TQ Website calendar v1.1'

    def items(self):
        events = list(Event.objects.all())
        special_courses = list(IrregularLesson.objects.filter(course__offering__type=Offering.Type.IRREGULAR).filter(course__active=True))

        return events + special_courses

    def item_title(self, item):
        if isinstance(item, Event):
            return item.name
        elif isinstance(item, IrregularLesson):
            return item.course.name

    def item_description(self, item):
        if isinstance(item, Event):
            description = item.name
            description += os.linesep
            description += item.safe_translation_getter("description", any_language=True) or ""

            price_string = item.format_prices()
            if price_string:
                description += os.linesep
                description += price_string
        elif isinstance(item, IrregularLesson):
            description = 'NOTE: You have to register in order to attend!'
            description += os.linesep
            description += os.linesep
            description += item.course.format_description()

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
        # remember to change this value when the calendar url changes
        if isinstance(item, Event):
            return 'https://tanzquotient.org/en/events/'
        elif isinstance(item, IrregularLesson):
            return 'https://tanzquotient.org/en/courses/'
        else:
            return 'https://tanzquotient.org/en/'

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
