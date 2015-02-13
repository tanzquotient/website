from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# Create your models here.

class Problem(models.Model):
    PRIORITY_NO = 0
    PRIORITY_LOW = 1
    PRIORITY_NORMAL = 2
    PRIORITY_HIGH = 3
    PRIORITIES = (
        (PRIORITY_NO, 'No priority'),
        (PRIORITY_LOW, 'Low'),
        (PRIORITY_NORMAL, 'Normal'),
        (PRIORITY_HIGH, 'High'),
    )

    datetime=models.DateTimeField(blank=False, null=False, auto_now=True, auto_now_add=True)
    tag = models.SlugField()
    message = models.TextField(blank=True, null=True)
    priority = models.IntegerField(default=PRIORITY_NO, choices=PRIORITIES)
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    content_type.label = u'Problematic model'
    content_type.short_description = u'Can refer to any model in the system.'
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return self.tag
    