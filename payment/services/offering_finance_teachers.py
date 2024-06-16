from decimal import Decimal
from typing import Sequence

from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

from courses.models import (
    Offering,
    CourseSubscriptionType,
    LessonOccurrence,
    Course,
    LessonOccurrenceTeach,
)


def offering_finance_teachers(
    offerings: Sequence[Offering], use_html: bool = False
) -> tuple[str, list, list, list, list, list, list]:
    """Exports a summary of the given ``offering`` concerning payment of teachers.

    Contains profile data relevant for payment of teachers and how many lesson at what rate to be paid.

    :param export_format: export format
    :param offerings: offerings to include in summary
    :return: response or ``None`` if format not supported
    """
    export_name = f'Salaries - {(offerings[0].name if len(offerings) == 1 else "Multiple Offerings")}'

    courses = _courses(offerings, use_html=use_html)
    teachings_tentative = _teachings(offerings, use_html=use_html, only_completed=False)
    teachings_completed = _teachings(offerings, use_html=use_html, only_completed=True)
    teachers_tentative = _teachers(offerings, use_html=use_html, only_completed=False)
    teachers_completed = _teachers(offerings, use_html=use_html, only_completed=True)
    personal_details = _personal_details(offerings)

    return (
        export_name,
        personal_details,
        teachings_tentative,
        teachings_completed,
        courses,
        teachers_tentative,
        teachers_completed,
    )


def _courses(offerings: Sequence[Offering], use_html: bool = False) -> list:
    courses = []

    header = [
        _("Course"),
        _("Teachers per lesson"),
        _("Status"),
    ]

    multiple_offerings = len(offerings) > 1
    if multiple_offerings:
        header.append(_("Offering"))

    if use_html:
        header.append(_("Actions"))

    courses.append(header)

    # get all courses in offerings
    course_list: list[Course] = (
        Course.objects.filter(offering__in=offerings)
        .exclude(subscription_type=CourseSubscriptionType.EXTERNAL)
        .all()
    )

    for course in course_list:
        status = []

        teachers_per_lesson = [
            l.teachers.count() for l in course.lesson_occurrences.all()
        ]

        if not course.is_over():
            status_text = _("Course is not over yet")
            status.append(
                status_text
                if not use_html
                else f"<span class='badge text-bg-info'>{status_text}</span>"
            )

        # check for lessons without teachers
        if course.is_over():
            lessons_without_teachers = teachers_per_lesson.count(0)
            if lessons_without_teachers:
                status_text = (
                    f"{_('Lessons without teachers')}: {lessons_without_teachers}"
                )
                status.append(
                    status_text
                    if not use_html
                    else f"<span class='badge text-bg-danger'>{status_text}</span>"
                )

        # check for lessons with more than two teachers
        lessons_with_more_than_two_teachers = [
            num_teachers > 2 for num_teachers in teachers_per_lesson
        ].count(True)
        if lessons_with_more_than_two_teachers:
            status_text = _("Some lessons have more than two teachers")
            status.append(
                status_text
                if not use_html
                else f"<span class='badge text-bg-danger'>{status_text}</span>"
            )

        # check for lessons with different number of teachers (excluding empty)
        nonzero_teachers_per_lesson = [
            num_teachers for num_teachers in teachers_per_lesson if num_teachers > 0
        ]
        if len(set(nonzero_teachers_per_lesson)) > 1:
            status_text = _("Not all lessons have the same number of teachers")
            status.append(
                status_text
                if not use_html
                else f"<span class='badge text-bg-warning'>{status_text}</span>"
            )

        # count how many lessons with a certain number of teachers
        lessons_for_x_teachers = dict()
        teachers_number_text = []
        for num_teachers in sorted(teachers_per_lesson):
            lessons_for_x_teachers[num_teachers] = (
                lessons_for_x_teachers.setdefault(num_teachers, 0) + 1
            )

        for num_teachers, num_lessons in lessons_for_x_teachers.items():
            if num_teachers > 0:
                status_text = (
                    f"{num_lessons} {_('lessons') if num_lessons != 1 else _('lesson')} "
                    f"{_('with')} {num_teachers} {_('teachers') if num_teachers != 1 else _('teacher')}"
                )
                teachers_number_text.append(status_text)

        # If we didn't find issues, let the user know
        if not status:
            status_text = _("Everything looks good")
            status.append(
                status_text
                if not use_html
                else f"<span class='badge text-bg-success'>{status_text}</span>"
            )

        # No status message except the fact that the course is marked as completed
        if course.completed:
            status_text = _("Course marked as completed")
            status = [
                (
                    status_text
                    if not use_html
                    else f"<span class='badge text-bg-info'>{status_text}</span>"
                )
            ]

        row = [
            (
                mark_safe(
                    f"<a href='{reverse('payment:course_teacher_presence', kwargs={'course': course.id})}'>{course.name}</a>"
                )
                if use_html
                else course.name
            ),
            (
                mark_safe("<br>".join(teachers_number_text))
                if use_html
                else ", ".join(teachers_number_text)
            ),
            mark_safe("<br/>".join(status)) if use_html else ", ".join(status),
        ]
        if multiple_offerings:
            row.append(course.offering)
        if use_html:
            row.append(
                mark_safe(
                    f"<button class='btn btn-secondary btn-sm disabled'>{_('Course completed')}</button>"
                    if course.completed
                    else f"<button data-course-id='{course.id}' class='btn btn-secondary btn-sm btn-completed'>{_('Mark as completed')}</button>"
                )
            )

        courses.append(row)

    if use_html:
        courses.append(
            [""] * (len(header) - 1)
            + [
                mark_safe(
                    f"<button data-course-id='all' class='btn btn-secondary btn-sm btn-completed'>{_('Mark all as completed')}</button>"
                )
            ]
        )
    return courses


def _teachings(
    offerings: Sequence[Offering], use_html: bool = False, only_completed: bool = True
) -> list:
    courses = []

    header = [
        _("First name"),
        _("Last name"),
        _("Courses"),
        _("Main teacher"),
        _("Hours"),
        _("Course Totals"),
    ]

    multiple_offerings = len(offerings) > 1
    if multiple_offerings:
        header += ["Offering"]
    courses.append(header)

    lesson_occurrences_filter = (
        Q(course__offering__in=offerings, course__completed=True)
        if only_completed
        else Q(course__offering__in=offerings)
    )

    # get all teachers in offerings
    teachers: list[User] = (
        User.objects.filter(
            lesson_occurrences__in=LessonOccurrence.objects.filter(
                lesson_occurrences_filter
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
        courses_filter = (
            Q(offering__in=offerings, completed=True)
            if only_completed
            else Q(offering__in=offerings)
        )
        teacher_courses = (
            Course.objects.filter(courses_filter)
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
                                lesson_occurrence.get_hours()
                                for lesson_occurrence in LessonOccurrence.objects.filter(
                                    course=course, teachers=teacher
                                ).all()
                            ],
                            Decimal(0),
                        )
                    )
                )

            total = sum(
                l.get_wage()
                for l in LessonOccurrenceTeach.objects.filter(
                    lesson_occurrence__course=course,
                    teacher=teacher,
                    lesson_occurrence__course__cancelled=False,
                ).all()
            )

            row += [
                (
                    mark_safe(
                        f"<a href='{reverse('payment:course_teacher_presence', kwargs={'course': course.id})}'>{course.name}</a>"
                    )
                    if use_html
                    else course.name
                ),
                _("Yes") if teacher in course.get_teachers() else _("No"),
                f"{hours}",
                f"{total:.2f} CHF",
            ]

            courses.append(row)

    return courses


def _teachers(
    offerings: Sequence[Offering], use_html: bool = False, only_completed: bool = True
) -> list:
    courses = []

    header = [
        _("First name"),
        _("Last name"),
        _("Hours"),
        _("Course Totals"),
    ]

    courses.append(header)

    lesson_occurrences_filter = (
        Q(course__offering__in=offerings, course__completed=True)
        if only_completed
        else Q(course__offering__in=offerings)
    )

    # get all teachers in offerings
    teachers: list[User] = (
        User.objects.filter(
            lesson_occurrences__in=LessonOccurrence.objects.filter(
                lesson_occurrences_filter
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
        courses_filter = (
            Q(offering__in=offerings, cancelled=False, completed=True)
            if only_completed
            else Q(offering__in=offerings, cancelled=False)
        )
        teacher_courses = (
            Course.objects.filter(courses_filter)
            .exclude(subscription_type=CourseSubscriptionType.EXTERNAL)
            .filter(lesson_occurrences__teachers=teacher)
            .distinct()
            .all()
            .order_by("offering_id", "name")
        )

        teacher_hours = Decimal(
            (
                sum(
                    [
                        lesson_occurrence.get_hours()
                        for lesson_occurrence in LessonOccurrence.objects.filter(
                            course__in=teacher_courses,
                            teachers=teacher,
                        ).all()
                    ],
                    Decimal(0),
                )
            )
        )
        teacher_total_salary = sum(
            l.get_wage()
            for l in LessonOccurrenceTeach.objects.filter(
                lesson_occurrence__course__in=teacher_courses,
                teacher=teacher,
            ).all()
        )

        courses.append(
            [
                teacher.first_name or "",
                teacher.last_name or "",
                f"{teacher_hours}",
                f"{teacher_total_salary:.2f} CHF",
            ]
        )

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
