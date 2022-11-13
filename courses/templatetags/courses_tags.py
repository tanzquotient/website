from django import template

from courses.services import get_offerings_by_year
from courses.models import *

register = template.Library()


@register.filter
def trans_weekday(key: str) -> str:
    return Weekday.WEEKDAYS_TRANSLATIONS[key]


@register.inclusion_tag(filename='courses/snippets/offerings_list.html')
def offerings_list(detail_url: str, only_public: bool = True) -> dict:
    offering_types = [OfferingType.REGULAR, OfferingType.IRREGULAR]
    return dict(
        detail_url=detail_url,
        offerings=get_offerings_by_year(offering_types, only_public),
        offering_types=offering_types,
    )
