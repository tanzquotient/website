from typing import Iterable

from courses.models import CourseSubscriptionType, Course, Style


def _course_filter_style(course: Course, style_name: str, filter_styles: Iterable[Style]) -> bool:
    if not style_name:
        return True

    if style_name.lower() == "all":
        return True

    if style_name.lower() == "other":
        for style in filter_styles:
            if course.has_style(style.name):
                return False
        return True

    return course.has_style(style_name)


def _course_filter_type(course: Course, subscription_type: str) -> bool:
    return subscription_type.lower() == course.subscription_type


def course_filter(course: Course, preview_mode: bool, subscription_type: str, style_name: str,
                  filter_styles: Iterable[Style]) -> bool:

    if not course.is_displayed(preview_mode):
        return False

    if course.is_over():
        return False

    return _course_filter_style(course, style_name, filter_styles) and _course_filter_type(course, subscription_type)
