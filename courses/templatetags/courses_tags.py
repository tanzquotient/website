from django import template
from django.template.defaultfilters import stringfilter
from courses.models import *

register = template.Library()

@register.filter
def trans_weekday(key):
    return WEEKDAYS_TRANS[key]
