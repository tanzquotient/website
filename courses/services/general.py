import logging
import re
from numbers import Number

from django.utils.translation import gettext as _

from courses import models as models
from courses.models import Course
from utils import TranslationUtils

log = logging.getLogger('tq')


def calculate_relevant_experience(user, course) -> list[Course]:
    """finds a list of courses the "user" did already and that are somehow relevant for "course\""""
    relevant_exp = [style.id for style in course.type.styles.all()]
    relevant_subscribes = models.Subscribe.objects\
        .filter(user=user, state__in=models.SubscribeState.ACCEPTED_STATES, course__type__styles__id__in=relevant_exp)\
        .exclude(course=course).order_by('course__type__level').distinct().all()
    return [s.course for s in relevant_subscribes]


def format_prices(price_with_legi: Number, price_without_legi: Number, price_special: str = None) -> str:
    if price_special:
        return price_special

    if not price_with_legi and not price_without_legi:
        return _('No entry fee')

    if not price_with_legi and price_without_legi:
        return f"{_('free for students')}, {_('otherwise {} CHF').format(price_without_legi)}"

    if price_with_legi == price_without_legi or (price_with_legi and not price_without_legi):
        return f"{price_with_legi} CHF"

    return f"{_('{} CHF for students').format(price_with_legi)}, {_('otherwise {} CHF').format(price_without_legi)}"


def model_attribute_language_fallback(model, attribute) -> str:
    return TranslationUtils.get_text_with_language_fallback(model, attribute)


INVALID_TITLE_CHARS = re.compile(r'[^\w\-_ ]', re.IGNORECASE | re.UNICODE)
