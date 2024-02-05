from datetime import datetime, time, date, timedelta
from typing import Optional

from django.db.models import QuerySet
from django.urls import reverse
from django.utils.html import strip_tags
from django_ical.views import ICalFeed

from .models import Event


class EventFeed(ICalFeed):
    product_id = "-//Tanzquotient Events//mxm.dk//"
    timezone = "UTC"

    def items(self) -> QuerySet[Event]:
        return Event.objects.filter(cancelled=False).all()

    def item_title(self, item: Event) -> str:
        return item.safe_translation_getter("name", any_language=True) or "Untitled"

    def item_description(self, event: Event) -> str:
        return "\n\n".join(
            [
                strip_tags(string)
                for string in [
                    event.description,
                    event.category.description if event.category is not None else None,
                    event.format_prices(),
                ]
                if string
            ]
        )

    def item_start_datetime(self, event: Event) -> [date | datetime]:
        if event.time_from is None:
            return event.date
        return datetime.combine(event.date, event.time_from or time.min)

    def item_end_datetime(self, event: Event) -> [date | datetime]:
        date_to = event.date_to or event.date
        if event.time_to is None:
            return date_to + timedelta(days=1)
        return datetime.combine(date_to, event.time_to or time.max)

    def item_location(self, event: Event) -> Optional[str]:
        if event.room is None:
            return None
        return event.room.name

    def item_link(self, event: Event) -> str:
        return reverse("events:detail", kwargs=dict(event_id=event.id))

    def item_guid(self, event: Event) -> str:
        return f"tanzquotient_event_{event.id}"
