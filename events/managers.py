from django.db import models
from datetime import datetime, timedelta


class DisplayedEventManager(models.Manager):
    def get_queryset(self):
        return super(DisplayedEventManager, self).get_queryset().filter(display=True)

    def future(self, delta_days=None):
        if delta_days:
            return self.filter(date__gte=datetime.today()).order_by('date', 'time_from').filter(
                date__lt=datetime.today() + timedelta(days=delta_days))
        else:
            return self.filter(date__gte=datetime.today()).order_by('date', 'time_from')

    def passed(self):
        return self.filter(date__lt=datetime.today()).order_by('date', 'time_from')


class SpecialEventManager(DisplayedEventManager):
    def get_queryset(self):
        return super(SpecialEventManager, self).get_queryset().filter(special=True)
