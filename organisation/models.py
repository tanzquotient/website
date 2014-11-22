from django.db import models

from django.conf import settings

import managers

# Create your models here.
class Function(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    email = models.EmailField(blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL)
    
    # position field for ordering columns (grappelli feature)
    position = models.PositiveSmallIntegerField("Position", default=0)
    class Meta:
        ordering = ['position']
        
    objects=managers.FunctionManager()
    
    def __unicode__(self):
        return u"{}".format(self.name)
