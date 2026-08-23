from typing import Callable, Iterable, TypeVar

from django.conf import settings
from django.core.cache import cache
from django.core.cache.utils import (
    TEMPLATE_FRAGMENT_KEY_TEMPLATE,
    make_template_fragment_key,
)

T = TypeVar("T")

DETAIL_CACHE_FRAGMENTS = ["course_info", "course_description", "room_disclaimer"]


def invalidate_course_list_cache() -> None:
    if hasattr(cache, "delete_pattern"):
        cache.delete_pattern(
            TEMPLATE_FRAGMENT_KEY_TEMPLATE % ("course_list_context", "*")
        )


def invalidate_course_reviews_cache() -> None:
    if hasattr(cache, "delete_pattern"):
        cache.delete_pattern(TEMPLATE_FRAGMENT_KEY_TEMPLATE % ("course_reviews", "*"))
        cache.delete_pattern(
            TEMPLATE_FRAGMENT_KEY_TEMPLATE % ("course_reviews_data", "*")
        )


def invalidate_course_detail_cache(course_ids: Iterable[int]) -> None:
    course_ids = list(course_ids)
    if not course_ids:
        return

    languages = [code for code, _ in settings.LANGUAGES]
    keys = [
        make_template_fragment_key(fragment, [course_id, lang])
        for fragment in DETAIL_CACHE_FRAGMENTS
        for course_id in course_ids
        for lang in languages
    ]
    cache.delete_many(keys)


def cached(cache_key: str, compute: Callable[[], T], timeout: int) -> T:
    result = cache.get(cache_key)
    if result is not None:
        return result

    result = compute()
    cache.set(cache_key, result, timeout)
    return result
