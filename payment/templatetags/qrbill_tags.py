from django import template

from courses.models import Subscribe
from payment.utils import create_qrbill_for_subscription, to_svg_string

register = template.Library()


@register.inclusion_tag(filename="qrbill/qrbill.html")
def qrbill_for_subscription(subscribe: Subscribe, qr_only: bool = False):
    return dict(qrbill=to_svg_string(create_qrbill_for_subscription(subscribe), qr_only))