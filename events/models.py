from django.db import models
from courses.models import *
from courses.services import format_prices

class Organise(models.Model):
    organiser = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='organising')
    event = models.ForeignKey('Event', related_name='organising')
    
    def __unicode__(self):
        return u"{} organises {}".format(self.organiser,self.event)
    
# Create your models here.
class Event(models.Model):
    name = models.CharField(max_length=255, blank=False)
    name.help_text = "The name of this event (e.g. 'Freies Tanzen')"
    date = models.DateField()
    time_from = models.TimeField(blank=True, null=True)
    time_to = models.TimeField(blank=True, null=True)
    room = models.ForeignKey(Room, related_name='events', blank=True, null=True, on_delete=models.SET_NULL)
    price_with_legi = models.FloatField(blank=True, null=True)
    price_with_legi.help_text = "Leave this empty for free entrance"
    price_without_legi = models.FloatField(blank=True, null=True)
    price_without_legi.help_text = "Leave this empty for free entrance"
    comment = models.TextField(blank=True, null=True)
    organisators = models.ManyToManyField(settings.AUTH_USER_MODEL, through=Organise, related_name='organising_events')
    description = HTMLField(blank=True, null=True)
    
    def format_organisators(self):
        return ', '.join(map(auth.get_user_model().get_full_name,self.organisators.all()))
    format_organisators.short_description="Organisators"
    
    def format_prices(self):
        return format_prices(self.price_with_legi,self.price_without_legi)
    format_prices.short_description="Prices"
    
    def format_time(self):
        if self.time_from and self.time_to:
            return  u"{}-{}".format(self.time_from.strftime("%H:%M") , self.time_to.strftime("%H:%M") )
        elif self.time_from:
            return  u"ab {}".format(self.time_from.strftime("%H:%M"))
        else:
            return  u"unbekannt"
            
    format_time.short_description="Time"
    
    
    # autocomplete fields (grappelli feature)
    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "name__icontains",)
          
    def __unicode__(self):
        return u"{}".format(self.name)
    
    class Meta:
        ordering = ['date','time_from','room']