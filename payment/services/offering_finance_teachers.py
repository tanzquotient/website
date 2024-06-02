from typing import Sequence
import datetime
from decimal import Decimal

from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.urls import reverse

from courses.models import (
    Offering,
    Teach,
    CourseSubscriptionType,
    LessonOccurrence,
    Course,
)


def offering_finance_teachers(
    offerings: Sequence[Offering], use_html: bool = False
) -> tuple[str, list, list]:
    """Exports a summary of the given ``offering`` concerning payment of teachers.

    Contains profile data relevant for payment of teachers and how many lesson at what rate to be paid.

    :param export_format: export format
    :param offerings: offerings to include in summary
    :return: response or ``None`` if format not supported
    """
    export_name = f'Salaries - {(offerings[0].name if len(offerings) == 1 else "Multiple Offerings")}'

    courses = _courses(offerings, use_html=use_html)
    personal_details = _personal_details(offerings)

    return export_name, personal_details, courses


def _courses(offerings: Sequence[Offering], use_html: bool = False) -> list:
    courses = []

    header = [
        _("First name"),
        _("Last name"),
        _("Courses"),
        _("Main teacher"),
        _("Hourly Wages"),
        _("Hours"),
        _("Course Totals"),
        _("Note"),
    ]

    multiple_offerings = len(offerings) > 1
    if multiple_offerings:
        header += ["Offering"]
    courses.append(header)

    # get all teachers in offerings
    teachers: list[User] = (
        User.objects.filter(
            lesson_occurrences__in=LessonOccurrence.objects.filter(
                course__offering__in=offerings
            )
            .exclude(course__subscription_type=CourseSubscriptionType.EXTERNAL)
            .all()
        )
        .distinct()
        .all()
        .order_by("first_name", "last_name")
    )

    for teacher in teachers:
        # get all courses for a teacher in offerings
        teacher_courses = (
            Course.objects.filter(offering__in=offerings)
            .exclude(subscription_type=CourseSubscriptionType.EXTERNAL)
            .filter(lesson_occurrences__teachers=teacher)
            .distinct()
            .all()
            .order_by("offering_id", "name")
        )

        for course in teacher_courses:
            row = [
                teacher.first_name or "",
                teacher.last_name or "",
            ]
            if multiple_offerings:
                row.append(course.offering or "")

            if course.cancelled:
                hours = 0
            else:
                hours = Decimal(
                    (
                        sum(
                            [
                                lesson_occurrence.duration()
                                for lesson_occurrence in LessonOccurrence.objects.filter(
                                    course=course, teachers=teacher
                                ).all()
                            ],
                            datetime.timedelta(),
                        ).total_seconds()
                        / 3600
                    ).__round__(2)
                )

            hourly_wage = teacher.profile.get_hourly_wage()
            total = hourly_wage * hours

            notes = []
            if course.cancelled:
                notes.append(_("Course cancelled"))
            else:
                if course.teaching.count() > 2:
                    notes.append(
                        _(
                            "Course with more than two teachers, please check who taught how many lessons."
                        )
                    )
                if course.get_confirmed_count() == 0:
                    notes.append(_("No participants"))

            row += [
                (
                    mark_safe(
                        f"<a href='{reverse('payment:course_teacher_presence', kwargs={'course': course.id})}'>{course.name}</a>"
                    )
                    if use_html
                    else course.name
                ),
                _("Yes") if teacher in course.get_teachers() else _("No"),
                f"{hourly_wage} CHF",
                f"{hours}",
                f"{total:.2f} CHF",
                "; ".join(map(str, notes)),
            ]

            courses.append(row)

    return courses


def _personal_details(offerings: Sequence[Offering]) -> list:
    personal_details = []
    header = [_("Last name"), _("First name"), _("E-mail"), _("Phone"), _("Address")]
    header += [
        _("Birth date"),
        _("Nationality"),
        _("Residence permit"),
        _("AHV number"),
        _("Zemis number"),
        _("IBAN"),
        _("Bank"),
    ]

    personal_details.append(header)

    teachers: list[User] = (
        User.objects.filter(
            lesson_occurrences__in=LessonOccurrence.objects.filter(
                course__offering__in=offerings
            )
            .exclude(course__subscription_type=CourseSubscriptionType.EXTERNAL)
            .all()
        )
        .distinct()
        .all()
        .order_by("first_name", "last_name")
    )

    for teacher in teachers:
        row = [
            teacher.first_name or "",
            teacher.last_name or "",
            teacher.email,
            teacher.profile.phone_number or "",
            str(teacher.profile.address) if teacher.profile.address else "",
            teacher.profile.birthdate,
            str(teacher.profile.nationality),
            teacher.profile.residence_permit,
            teacher.profile.ahv_number,
            teacher.profile.zemis_number,
        ]

        if teacher.profile.bank_account:
            row += [
                teacher.profile.bank_account.iban,
                teacher.profile.bank_account.bank_info_str(),
            ]
        else:
            row += [""] * 2

        personal_details.append(row)

    return personal_details
