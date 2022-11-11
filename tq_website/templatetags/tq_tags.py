from django import template
from django.urls import reverse

register = template.Library()


@register.inclusion_tag(filename='snippets/download.html')
def download_button(url: str, **kwargs: dict):

    return dict(
        url=reverse(url, kwargs=kwargs)
    )


@register.inclusion_tag(filename='snippets/table.html')
def table(data: list):
    if len(data) <= 1:
        return dict()

    return dict(
        header=data[0],
        rows=data[1:]
    )

