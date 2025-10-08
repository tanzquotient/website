from numbers import Number
from typing import Iterable, Any
from uuid import uuid4

from django import template

register = template.Library()


def fence_helper(value, s):
    return s + value + s


@register.filter(needs_autoescape=False)
def fence(value, s):
    if isinstance(value, str):
        return fence_helper(value, s)
    elif isinstance(value, list):
        return map(lambda v: fence_helper(v, s), value)
    else:
        return fence_helper(str(value), s)


@register.filter(name="lookup")
def lookup(value: dict | list, arg: object) -> object:
    return value[arg]


@register.simple_tag
def concat_all(*args: Iterable[Any]) -> str:
    return "".join(map(str, args))


@register.filter(name="abs")
def absolute(value: int | float) -> int | float:
    return abs(value)


@register.filter(name="minus")
def minus(a: int | float, b: int | float) -> int | float:
    return a - b


@register.filter
def append_uuid(value):
    return str(value) + str(uuid4())


@register.simple_tag
def git_head():
    import subprocess

    label = (
        subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
        .strip()
        .decode()
    )
    return label
