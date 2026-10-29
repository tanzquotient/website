import base64
import hashlib
from functools import cache

import shortuuid
from django import template
from django.conf import settings
from django.urls import reverse
from django.utils.html import format_html
from plotly.offline import get_plotlyjs, get_plotlyjs_version

register = template.Library()


@register.inclusion_tag(filename="snippets/download.html")
def download_button(url: str, **kwargs: dict):
    return {"url": reverse(url, kwargs=kwargs)}


@register.inclusion_tag(filename="snippets/table.html")
def table(data: list):
    if len(data) <= 1:
        return {}

    return {"header": data[0], "rows": data[1:]}


@register.inclusion_tag(filename="snippets/collapsible_list.html")
def collapsible_list(items: list, limit: int, item_template: str):
    limit = limit or len(items)
    return {
        "id": f"collapse_{shortuuid.uuid()}",
        "has_items": (len(items) > 0),
        "can_expand": (len(items) > limit),
        "always_visible_items": items[:limit],
        "collapsible_items": items[limit:],
        "item_template": item_template,
    }


@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")


@register.simple_tag
@cache
def plotly_js():
    # Load the plotly.js version the installed plotly package generates figures for
    integrity = base64.b64encode(hashlib.sha256(get_plotlyjs().encode()).digest())
    return format_html(
        '<script src="https://cdn.plot.ly/plotly-{}.min.js" integrity="sha256-{}" '
        'crossorigin="anonymous"></script>',
        get_plotlyjs_version(),
        integrity.decode(),
    )
