from collections import defaultdict
from functools import cache
from typing import Iterable

from django.contrib.auth.models import User
from django.db import transaction

from . import StyleLevel
from ...models import (
    SubscribeState,
    Style,
    SkillDanceLevel,
    LessonOccurrence,
)


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


def eligible_lessons(
    user: User, lessons: Iterable[LessonOccurrence]
) -> list[LessonOccurrence]:
    dance_levels = get_saved_dance_levels(user)
    return [l for l in lessons if _is_eligible_for_lesson(dance_levels, l)]


def is_eligible_for_lesson(user: User, lesson: LessonOccurrence) -> bool:
    dance_levels = get_saved_dance_levels(user)
    return _is_eligible_for_lesson(dance_levels, lesson)


def _is_eligible_for_lesson(
    user_dance_levels: list[StyleLevel], lesson: LessonOccurrence
) -> bool:
    course_type = lesson.course.type
    required_level = course_type.level or 1
    if lesson.id == lesson.course.first_lesson.id:
        required_level -= 1

    styles = course_type.styles.all()
    return _has_required_level(user_dance_levels, styles, required_level)


def _has_required_level(
    user_dance_levels: list[StyleLevel],
    styles: Iterable[Style],
    course_level: int,
) -> bool:
    for style in styles:
        if not _has_level(style, course_level, user_dance_levels):
            return False

    return True


def _has_level(style: Style, level: int, dance_levels: list[StyleLevel]) -> bool:
    if level == 0:
        return True

    level_for_style = _get_level_for_style(style, dance_levels)
    if level_for_style >= level:
        return True  # Level for style is high enough

    # Maybe the user is still eligible, based on the style's children.
    # E.g., if someone has Standard level 5, and the course requires Waltz level 4,
    # they are eligible.

    child_styles = _style_children(style)
    if not child_styles:
        return False  # level not sufficient, and no children => cannot be eligible

    # Eligible if level for each child style is sufficient.
    return all(_has_level(child, level, dance_levels) for child in child_styles)


def _get_level_for_style(style: Style, dance_levels: list[StyleLevel]) -> int:
    for dance_level in dance_levels:
        if dance_level.style == style:
            return dance_level.level
    return 0


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
    for child in _style_children(style):
        for descendant in _style_descendants(child):
            descendants.append(descendant)
    return descendants


@cache
def _style_children(style: Style) -> list[Style]:
    return list(style.children.all())
