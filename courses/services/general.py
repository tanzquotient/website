import logging
import re

from django.utils.translation import gettext as _

from courses import models as models
from utils import TranslationUtils

log = logging.getLogger('tq')


def calculate_relevant_experience(user, course):
    '''finds a list of courses the "user" did already and that are somehow relevant for "course"'''
    relevant_exp = [style.id for style in course.type.styles.all()]
    return [s.course for s in
            models.Subscribe.objects.filter(user=user, state__in=models.SubscribeState.ACCEPTED_STATES,
                                            course__type__styles__id__in=relevant_exp).exclude(
                course=course).order_by('course__type__level').distinct().all()]


def format_prices(price_with_legi, price_without_legi, price_special=None):
    if price_special:
        return price_special
    elif price_with_legi and price_without_legi:
        if price_with_legi == price_without_legi:
            r = "{} CHF".format(price_with_legi.__str__())
        else:
            r = "mit Legi {} / sonst {} CHF".format(price_with_legi.__str__(), price_without_legi.__str__())
    elif price_without_legi:
        r = "mit Legi freier Eintritt (sonst {} CHF)".format(price_without_legi.__str__())
    else:
        r = _('No entry fee')
    return r


def model_attribute_language_fallback(model, attribute):
    return TranslationUtils.get_text_with_language_fallback(model, attribute)


INVALID_TITLE_CHARS = re.compile(r'[^\w\-_ ]', re.IGNORECASE | re.UNICODE)