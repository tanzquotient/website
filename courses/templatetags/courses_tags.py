from django import template

from courses.models import *

register = template.Library()


@register.filter
def trans_weekday(key: str) -> str:
    return Weekday.WEEKDAYS_TRANSLATIONS[key]
