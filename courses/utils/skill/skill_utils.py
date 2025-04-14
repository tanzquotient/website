from functools import cache
from typing import Iterable

from django.contrib.auth.models import User

from ...models import CourseType, SubscribeState


def calculate_unlocked_course_types(user: User) -> Iterable[CourseType]:
    participated_types = {
        subscription.course.type
        for subscription in user.subscriptions.all()
        if subscription.state in SubscribeState.ACCEPTED_STATES
    }
    return {
        course_type
        for participated_type in participated_types
        for course_type in transitive_predecessors(participated_type)
    }


@cache
def transitive_predecessors(course_type: CourseType) -> set[CourseType]:
    predecessors: set[CourseType] = set()
    predecessors.add(course_type)
    for predecessor in course_type.predecessors.all():
        if predecessor not in predecessors:
            for transitive in transitive_predecessors(predecessor):
                predecessors.add(transitive)
    return predecessors
