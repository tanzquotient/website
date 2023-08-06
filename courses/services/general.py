import logging
import re
from numbers import Number
from typing import Iterable

from django.utils.translation import gettext as _

from courses.models import Subscribe, SubscribeState, OfferingType, Course
from utils import TranslationUtils

log = logging.getLogger("tq")


def calculate_relevant_experience(self: Subscribe) -> Iterable[Course]:
    """returns similar courses that the user did before in the system"""

    relevant_exp = [style.id for style in self.course.type.styles.all()]

    relevant_courses = [
        subscription.course
        for subscription in self.user.subscriptions.all()
        if subscription.state in SubscribeState.ACCEPTED_STATES
        and any(
            [
                style.id in relevant_exp
                for style in subscription.course.type.styles.all()
            ]
        )
    ]

    return dict.fromkeys(
        sorted(
            relevant_courses,
            key=lambda course: (
                10 if course.offering.type == OfferingType.REGULAR else 1
            )
            * (course.type.level or 0),
            reverse=True,
        )
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
