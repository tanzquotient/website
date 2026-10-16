from collections.abc import Iterable
from typing import TypeVar

T = TypeVar("T")


def optional_min(elements: Iterable[T | None]) -> T | None:
    return min(filter(lambda e: e is not None, elements), default=None)


def optional_max(elements: Iterable[T | None]) -> T | None:
    return max(filter(lambda e: e is not None, elements), default=None)
