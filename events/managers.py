from datetime import datetime, timedelta

from django.db import models


class DisplayedEventQuerySet(models.QuerySet):
    def visible_to(self, user):
        from .models.event import Event

        if Event.user_can_view_unpublished(user):
            return self
        return self.filter(published=True)

    def future(self, delta_days=None, limit=None):
        queryset = self.filter(date__gte=datetime.today()).order_by("date", "time_from")

        if delta_days:
            queryset = queryset.filter(
                date__lte=datetime.today() + timedelta(days=delta_days)
            )
        if limit:
            queryset = queryset[:limit]

        return queryset

    def past(self):
        return self.filter(date__lt=datetime.today()).order_by("date", "time_from")


class DisplayedEventManager(models.Manager.from_queryset(DisplayedEventQuerySet)):
    def get_queryset(self):
        return super().get_queryset().filter(display=True)


class SpecialEventManager(DisplayedEventManager):
    def get_queryset(self):
        return super().get_queryset().filter(special=True)
