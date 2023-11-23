from collections import defaultdict
from decimal import Decimal
from typing import Iterable

from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from courses.models import Teach


def get_teachers_overview_data() -> list[list]:
    grouped_teachings = defaultdict(lambda: defaultdict(list))
    for teaching in (
        Teach.objects.order_by("teacher__first_name", "teacher__last_name")
        .prefetch_related(
            "teacher",
            "course__irregular_lessons",
            "course__regular_lessons",
            "course__regular_lessons__exceptions",
            "course__offering__period",
            "course__offering__period__cancellations",
            "course__period",
            "course__period__cancellations",
        )
        .all()
    ):
        if (
            teaching.course.is_external()
            or teaching.course.cancelled
            or not teaching.course.get_lessons()
        ):
            continue

        first_lesson_date = teaching.course.get_first_lesson_date()
        year = str(first_lesson_date.year) if first_lesson_date else _("unknown year")
        grouped_teachings[teaching.teacher_id][year].append(teaching)

    rows = []

    years = sorted(
        {year for group in grouped_teachings.values() for year in group.keys()}
    )

    header = (
        [_("First name"), _("Last name")] + years + [_("Total years"), _("Total hours")]
    )

    for grouped_by_year in grouped_teachings.values():
        teacher: User = list(grouped_by_year.values())[0][0].teacher
        row = [teacher.first_name, teacher.last_name]

        for year in years:
            row.append(sum_of_course_hours(grouped_by_year.get(year, [])) or "-")

        # Number of years the teacher has been teaching
        # (counting unknown year as one year)
        row.append(len(grouped_by_year.values()))

        row.append(
            sum_of_course_hours(
                [
                    teaching
                    for teachings in grouped_by_year.values()
                    for teaching in teachings
                ]
            )
        )

        rows.append(row)

    # Sort by last column (total hours) descending
    sorted_rows = sorted(rows, key=lambda r: r[-1], reverse=True)

    return [header] + sorted_rows


def sum_of_course_hours(teachings: Iterable[Teach]) -> Decimal:
    return sum(
        [teaching.course.get_total_hours() for teaching in teachings],
        Decimal(0),
    )
