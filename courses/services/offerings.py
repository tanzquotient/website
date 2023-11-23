from collections import defaultdict
from datetime import date, time
from typing import Collection

from django.db.models import Q, QuerySet
from django.http import Http404
from django.utils import dateformat
from django.utils.translation import gettext as _

from courses import models as models
from courses.managers import CourseManager
from courses.models import (
    Offering,
    OfferingType,
    Weekday,
    Course,
)
from courses.services.general import log


def get_all_offerings():
    return Offering.objects.order_by("period__date_from", "-active")


def get_offerings_to_display(preview: bool = False) -> QuerySet[Offering]:
    """return offerings that have display flag on and order them by start date in ascending order"""

    queryset = Offering.objects.exclude(type=OfferingType.PARTNER)

    if preview:
        queryset = queryset.filter(Q(display=True) | Q(preview=True))
    else:
        queryset = queryset.filter(display=True)

    return queryset.select_related("period").order_by("order", "-period__date_from")


def get_offerings_by_year(
    offering_types: Collection[OfferingType], only_public: bool = True
):
    offerings_dict = defaultdict(lambda: defaultdict(list))
    for offering in Offering.objects.filter(type__in=offering_types).all():
        if only_public and not offering.is_public():
            continue
        offerings_dict[offering.get_start_year()][offering.type].append(offering)

    return sorted(
        [
            (year, offerings_by_type)
            for year, offerings_by_type in offerings_dict.items()
        ],
        key=lambda t: t[0] or 3000,
        reverse=True,
    )


def course_sort_key(course: Course) -> tuple:
    default_date = date(year=9999, month=1, day=1)
    default_time = time(hour=23, minute=59, second=59)
    first_date = course.get_first_lesson_date() or default_date
    first_regular = course.get_first_regular_lesson()
    first_irregular = course.get_first_irregular_lesson()
    first_time = (
        first_regular.time_from
        if first_regular
        else (first_irregular.time_from if first_irregular else default_time)
    )

    if course.offering.type != OfferingType.REGULAR:
        return first_date, first_time

    return course.type.title, first_time


def get_sections(offering, course_filter=None):
    offering_sections = []
    course_set = offering.course_set

    if not course_filter:
        course_filter = lambda c: True

    if not offering.group_into_sections:
        courses = sorted(
            [c for c in course_set.all() if course_filter(c)],
            key=course_sort_key,
        )
        offering_sections.append(dict(courses=courses))
    elif offering.type == OfferingType.REGULAR:
        for w, w_name in Weekday.CHOICES:
            courses_on_weekday = [
                c for c in CourseManager.weekday(course_set, w) if course_filter(c)
            ]
            if courses_on_weekday:
                offering_sections.append(
                    {
                        "section_title": Weekday.WEEKDAYS_TRANSLATIONS[w],
                        "courses": sorted(courses_on_weekday, key=course_sort_key),
                    }
                )

        courses_without_weekday = [
            c for c in CourseManager.weekday(course_set, None) if course_filter(c)
        ]
        if courses_without_weekday:
            offering_sections.append(
                {
                    "section_title": _("Irregular weekday"),
                    "courses": sorted(courses_without_weekday, key=course_sort_key),
                }
            )

    elif offering.type in [OfferingType.IRREGULAR, OfferingType.PARTNER]:
        courses_by_month = CourseManager.by_month(course_set)
        for d, courses in courses_by_month:
            if d is None:
                section_title = _("Unknown month")
            elif 1 < d.month <= 12:
                # use the django formatter for date objects
                section_title = dateformat.format(d, "F Y")
            else:
                section_title = ""
            # filter out undisplayed courses if not staff user
            courses = [c for c in courses if course_filter(c)]
            # tracks if at least one period of a course is set (it should be displayed on page)
            deviating_period = False
            for c in courses:
                if c.period:
                    deviating_period = True
                    break

            if courses:
                offering_sections.append(
                    {
                        "section_title": section_title,
                        "courses": sorted(courses, key=course_sort_key),
                        "hide_period_column": not deviating_period,
                    }
                )
    else:
        message = "unsupported offering type"
        log.error(message)
        raise Http404(message)

    return offering_sections


def get_current_active_offering():
    return (
        models.Offering.objects.filter(active=True)
        .order_by("period__date_from")
        .first()
    )


def get_subsequent_offering():
    res = (
        models.Offering.objects.filter(period__date_from__gte=date.today())
        .order_by("period__date_from")
        .all()
    )
    if len(res) > 0:
        return res[0]
    else:
        return None
