import logging
import re
from collections import Counter
from numbers import Number
from typing import Iterable

from django.utils.translation import gettext as _

from courses.models import Subscribe, SubscribeState, CourseType
from utils import TranslationUtils

log = logging.getLogger("tq")


def calculate_relevant_experience(self: Subscribe) -> Iterable[tuple[CourseType, int]]:
    """returns similar courses that the user did before in the system"""

    relevant_exp = [style.id for style in self.course.type.styles.all()]

    relevant_courses = Counter(
        [
            subscription.course.type
            for subscription in self.user.subscriptions.all()
            if subscription.state in SubscribeState.ACCEPTED_STATES
            and any(
                [
                    related_style.id in relevant_exp
                    for style in subscription.course.type.styles.all()
                    for related_style in style.related()
                ]
            )
        ]
    )

    return sorted(
        relevant_courses.items(),
        key=lambda item: (item[0].level or 0, item[1]),
        reverse=True,
    )


def format_prices(
    price_with_legi: Number, price_without_legi: Number, price_special: str = None
) -> str:
    if price_special:
        return price_special

    if not price_with_legi and not price_without_legi:
        return _("No entry fee")

    if not price_with_legi and price_without_legi:
        return (
            _("free for students")
            + ", "
            + _("otherwise {:g} CHF").format(price_without_legi)
        )

    if price_with_legi == price_without_legi or (
        price_with_legi and not price_without_legi
    ):
        return f"{price_with_legi:g} CHF"

    return (
        _("{:g} CHF for students").format(price_with_legi)
        + ", "
        + _("otherwise {:g} CHF").format(price_without_legi)
    )


def model_attribute_language_fallback(model, attribute) -> str:
    return TranslationUtils.get_text_with_language_fallback(model, attribute)


INVALID_TITLE_CHARS = re.compile(r"[^\w\-_ ]", re.IGNORECASE | re.UNICODE)
