import uuid

import shortuuid
from django import template
from django.urls import reverse

register = template.Library()


@register.inclusion_tag(filename="snippets/download.html")
def download_button(url: str, **kwargs: dict):
    return dict(url=reverse(url, kwargs=kwargs))


@register.inclusion_tag(filename="snippets/table.html")
def table(data: list):
    if len(data) <= 1:
        return dict()

    return dict(header=data[0], rows=data[1:])


@register.inclusion_tag(filename="snippets/collapsible_list.html")
def collapsible_list(items: list, limit: int, item_template: str):
    limit = limit or len(items)
    return dict(
        id=f"collapse_{shortuuid.uuid()}",
        has_items=(len(items) > 0),
        can_expand=(len(items) > limit),
        always_visible_items=items[:limit],
        collapsible_items=items[limit:],
        item_template=item_template,
    )
