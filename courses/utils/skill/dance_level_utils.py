from collections import defaultdict
from functools import cache
from typing import Iterable

from django.contrib.auth.models import User
from django.db import transaction

from . import StyleLevel
from ...models import SubscribeState, Style, SkillDanceLevel


def recompute_dance_levels_for_user(user: User) -> None:
    skill = user.skill
    new_levels = calculate_dance_levels_for_user(user=user)
    with transaction.atomic():
        SkillDanceLevel.objects.filter(skill=skill).delete()
        SkillDanceLevel.objects.bulk_create(
            [
                SkillDanceLevel(skill=skill, level=item.level, style=item.style)
                for item in new_levels
            ]
        )


def calculate_dance_levels_for_user(user: User) -> list[StyleLevel]:
    return combine_dance_levels(
        get_saved_dance_levels(user)
        + get_dance_levels_from_participating(user)
        + get_dance_levels_from_teaching(user)
    )


def get_dance_levels_from_teaching(user: User) -> list[StyleLevel]:
    return [
        StyleLevel(
            style=style,
            # Assume teachers are 10 levels above their courses
            level=(teaching.course.type.level or 0) + 10,
        )
        for teaching in user.teaching_courses.prefetch_related(
            "course__type__styles"
        ).all()
        for style in teaching.course.type.styles.all()
        if not teaching.course.cancelled
    ]


def get_dance_levels_from_participating(user: User) -> list[StyleLevel]:
    return [
        StyleLevel(style=style, level=subscription.course.type.level or 1)
        for subscription in user.subscriptions.prefetch_related(
            "course__type__styles"
        ).all()
        for style in subscription.course.type.styles.all()
        if subscription.state in SubscribeState.ACCEPTED_STATES
    ]


def get_saved_dance_levels(user: User) -> list[StyleLevel]:
    return [
        StyleLevel(style=dance_level.style, level=dance_level.level)
        for dance_level in user.skill.dance_levels.prefetch_related("style").all()
    ]


def combine_dance_levels(dance_levels: Iterable[StyleLevel]) -> list[StyleLevel]:

    # Merge by style, only keep the highest level
    level_by_style: dict[Style, int] = defaultdict(int)
    for item in dance_levels:
        style = item.style
        level_by_style[style] = max(level_by_style[style], item.level)

    # Update level for children.
    # E.g., if someone has Standard level 5, this ensures they will also get at least
    # level 5 for Waltz, Tango, etc.
    items_copy = list(level_by_style.items())
    for style, level in items_copy:
        for child in _style_descendants(style):
            level_by_style[child] = max(level_by_style[child], level)

    return [StyleLevel(style=s, level=l) for s, l in level_by_style.items()]


@cache
def _style_descendants(style: Style) -> list[Style]:
    descendants = [style]
    for child in style.children.all():
        for descendant in _style_descendants(child):
            descendants.append(descendant)
    return descendants
