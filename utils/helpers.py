from typing import Optional, Iterable, TypeVar

T = TypeVar("T")


def optional_min(elements: Iterable[Optional[T]]) -> Optional[T]:
    return min(filter(lambda e: e is not None, elements), default=None)


def optional_max(elements: Iterable[Optional[T]]) -> Optional[T]:
    return max(filter(lambda e: e is not None, elements), default=None)
