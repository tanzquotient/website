from django.db import models

class EventManager(models.Manager):
    def displayed(self):
        return self.filter(display=True)
    
class SpecialEventManager(EventManager):
    def get_queryset(self):
        return super(SpecialEventManager, self).get_queryset().filter(special=True)
