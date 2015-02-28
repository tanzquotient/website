from django.db import models
from datetime import datetime

class DisplayedEventManager(models.Manager):
    def get_queryset(self):
        return super(DisplayedEventManager, self).get_queryset().filter(display=True)
    
    def future(self, delta=None):
        if delta:
            return self.filter(date__gte=datetime.today()).filter(date__lt=datetime.today()+delta)
        else:
            return self.filter(date__gte=datetime.today())
    
    def passed(self):
        return self.filter(date__lt=datetime.today())
    
class SpecialEventManager(DisplayedEventManager):
    def get_queryset(self):
        return super(SpecialEventManager, self).get_queryset().filter(special=True)
