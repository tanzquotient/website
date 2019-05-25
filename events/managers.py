from django.db import models
from datetime import datetime, timedelta


class DisplayedEventManager(models.Manager):
    def get_queryset(self):
        return super(DisplayedEventManager, self).get_queryset().filter(display=True)

    def future(self, delta_days=None, limit=None):
        queryset = self.filter(date__gte=datetime.today()).order_by('date', 'time_from')

        if delta_days:
            queryset = queryset.filter(date__lte=datetime.today() + timedelta(days=delta_days))
        if limit:
            queryset = queryset[:limit]

        return queryset

    def passed(self):
        return self.filter(date__lt=datetime.today()).order_by('date', 'time_from')


class SpecialEventManager(DisplayedEventManager):
    def get_queryset(self):
        return super(SpecialEventManager, self).get_queryset().filter(special=True)
