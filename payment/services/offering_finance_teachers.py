from collections.abc import Sequence
from decimal import Decimal

from django.contrib.auth.models import User
from django.db.models import Count, Prefetch, Q
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from courses.models import (
    Course,
    CourseSubscriptionType,
    LessonOccurrence,
    LessonOccurrenceTeach,
    Offering,
)


def offering_finance_teachers(
    offerings: Sequence[Offering], use_html: bool = False
) -> tuple[str, list[dict]]:
    """Exports a summary of the given ``offering`` concerning payment of teachers.

    Contains profile data relevant for payment of teachers and how many lesson at what
     rate to be paid.

    :param use_html: whether html is supported for the output
    :param offerings: offerings to include in summary
    :return: response or ``None`` if format not supported
    """
    export_name = f"Salaries - {(offerings[0].name if len(offerings) == 1 else 'Multiple Offerings')}"

    courses = _courses(offerings, use_html=use_html)
    teachings_tentative = _teachings(offerings, use_html=use_html, only_completed=False)
    teachings_completed = _teachings(offerings, use_html=use_html, only_completed=True)
    teachers_tentative = _teachers(offerings, only_completed=False)
    teachers_completed = _teachers(offerings, only_completed=True)
    personal_details = _personal_details(offerings)

    return (
        export_name,
        [
            {"data": courses, "name": "Courses"},
            {"data": teachers_completed, "name": "Teachers Summary"},
            {"data": teachings_completed, "name": "Teachers by Course"},
            {"data": personal_details, "name": "Personal Data"},
            {"data": teachers_tentative, "name": "[Tentative] Teachers Summary"},
            {"data": teachings_tentative, "name": "[Tentative] Teachers by course"},
        ],
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

    # get all courses in offerings, with the number of teachers of each lesson
    course_list: list[Course] = (
        Course.objects.filter(offering__in=offerings)
        .exclude(subscription_type=CourseSubscriptionType.EXTERNAL)
        .select_related("period", "offering__period")
        .prefetch_related(
            Prefetch(
                "lesson_occurrences",
                queryset=LessonOccurrence.objects.annotate(
                    num_teachers=Count("teachers")
                ),
            )
        )
        .all()
    )

    any_course_without_teachers = False
    for course in course_list:
        teachers_per_lesson = [l.num_teachers for l in course.lesson_occurrences.all()]
        course_without_teachers = 0 in teachers_per_lesson
        any_course_without_teachers |= course_without_teachers

        row = [
            (
                mark_safe(
                    f"<a href='{reverse('payment:course_teacher_presence', kwargs={'course': course.id})}'>{course.name}</a>"
                )
                # if the course is cancelled, there is no teacher presence form
                if use_html and not course.cancelled
                else course.name
            ),
            _format_list(
                _get_num_teachers_per_lesson(teachers_per_lesson=teachers_per_lesson),
                use_html=use_html,
            ),
            _format_list(
                _get_course_status(
                    course=course,
                    teachers_per_lesson=teachers_per_lesson,
                    use_html=use_html,
                ),
                use_html=use_html,
            ),
        ]
        if multiple_offerings:
            row.append(course.offering)
        if use_html:
            row.append(
                mark_safe(
                    f"<button class='btn btn-secondary btn-sm disabled'>{_('Course completed')}</button>"
                    if course.completed
                    else f"<button {'data-course-without-teachers=true' if course_without_teachers else ''} data-course-id='{course.id}' class='btn btn-secondary btn-sm btn-completed'><i class='bi bi-person-fill-lock'></i> {_('Mark as completed')}</button>"
                )
            )

        courses.append(row)

    if use_html:
        courses.append(
            [""] * (len(header) - 1)
            + [
                mark_safe(
                    f"<button {'data-course-without-teachers=true' if any_course_without_teachers else ''} data-course-id='all' class='btn btn-secondary btn-sm btn-completed'><i class='bi bi-person-fill-lock'></i> {_('Mark all as completed')}</button>"
                )
            ]
        )
    return courses


def _get_course_status(
    course: Course, teachers_per_lesson: list[int], use_html: bool
) -> list[str]:
    def _format_status(status_text: str, text_class: str) -> str:
        return (
            status_text
            if not use_html
            else f"<span class='badge text-bg-{text_class}'>{status_text}</span>"
        )

    status = []

    # if the course is cancelled, just write that as status
    if course.cancelled:
        return [_format_status(_("Course cancelled"), "secondary")]

    # No status message except the fact that the course is marked as completed
    if course.completed:
        return [_format_status(_("Course marked as completed"), "success")]

    if not course.is_over():
        status.append(_format_status(_("Course is not over yet"), "secondary"))

    # check for lessons without teachers
    if course.is_over():
        lessons_without_teachers = teachers_per_lesson.count(0)
        if lessons_without_teachers:
            status.append(
                _format_status(
                    f"{_('Lessons without teachers')}: {lessons_without_teachers}",
                    "danger",
                ),
            )

    # check for lessons with more than two teachers
    lessons_with_more_than_two_teachers = [
        num_teachers > 2 for num_teachers in teachers_per_lesson
    ].count(True)
    if lessons_with_more_than_two_teachers:
        status.append(
            _format_status(_("Some lessons have more than two teachers"), "danger"),
        )

    # check for lessons with different number of teachers (excluding empty)
    nonzero_teachers_per_lesson = [
        num_teachers for num_teachers in teachers_per_lesson if num_teachers > 0
    ]
    if len(set(nonzero_teachers_per_lesson)) > 1:
        status.append(
            _format_status(
                _("Not all lessons have the same number of teachers"), "warning"
            ),
        )

    # If we didn't find issues, let the user know
    if not status:
        status = [_format_status(_("Everything looks good"), "info")]

    return status


def _get_num_teachers_per_lesson(teachers_per_lesson: list[int]) -> list[str]:
    # count how many lessons with a certain number of teachers
    lessons_for_x_teachers = {}
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

    return teachers_number_text


def _format_list(text_list: list, use_html: bool) -> str:
    return (
        mark_safe("<br/>".join(text_list))
        if use_html
        else ", ".join(map(str, text_list))
    )


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

    teaches_by_teacher = _teaches_by_teacher_and_course(offerings, only_completed)
    for teacher, teacher_courses in teaches_by_teacher.items():
        for course, teaches in teacher_courses.items():
            hours = Decimal(
                sum((t.lesson_occurrence.get_hours() for t in teaches), Decimal(0))
            )
            total = sum(t.get_wage() for t in teaches)

            row = [
                teacher.first_name or "",
                teacher.last_name or "",
                (
                    mark_safe(
                        f"<a href='{reverse('payment:course_teacher_presence', kwargs={'course': course.id})}'>{course.name}</a>"
                    )
                    if use_html
                    else course.name
                ),
                _("Yes") if teacher.id in course.get_teacher_ids() else _("No"),
                f"{hours}",
                f"{total:.2f} CHF",
            ]
            if multiple_offerings:
                row.append(course.offering or "")

            courses.append(row)

    return courses


def _teachers(offerings: Sequence[Offering], only_completed: bool = True) -> list:
    all_completed = all(
        course.completed for course in Course.objects.filter(offering__in=offerings)
    )

    if only_completed and not all_completed:
        return [
            [_("Note")],
            [
                _(
                    "Some courses are not marked as completed yet. "
                    "Final data can not be shown."
                )
            ],
        ]

    courses = []

    header = [
        _("First name"),
        _("Last name"),
        _("Hours"),
        _("Course Totals"),
    ]

    courses.append(header)

    teaches_by_teacher = _teaches_by_teacher_and_course(offerings, only_completed)
    for teacher, teacher_courses in teaches_by_teacher.items():
        teaches = [
            t for course_teaches in teacher_courses.values() for t in course_teaches
        ]

        teacher_hours = Decimal(
            sum((t.lesson_occurrence.get_hours() for t in teaches), Decimal(0))
        )
        teacher_total_salary = sum(t.get_wage() for t in teaches)

        courses.append(
            [
                teacher.first_name or "",
                teacher.last_name or "",
                f"{teacher_hours}",
                f"{teacher_total_salary:.2f} CHF",
            ]
        )

    return courses


def _teaches_by_teacher_and_course(
    offerings: Sequence[Offering], only_completed: bool
) -> dict[User, dict[Course, list[LessonOccurrenceTeach]]]:
    """Groups the teaches of paid courses in ``offerings`` by teacher and course.

    Teachers are ordered by name, their courses by offering and name, and the teaches
    of a course by lesson start. Everything is loaded with a constant number of
    queries, since querying per teacher and course is too slow for big offerings.
    """
    courses_filter = (
        Q(offering__in=offerings, completed=True)
        if only_completed
        else Q(offering__in=offerings)
    )
    courses: dict[int, Course] = {
        course.id: course
        for course in Course.objects.filter(courses_filter)
        .exclude(subscription_type=CourseSubscriptionType.EXTERNAL)
        .exclude(cancelled=True)
        .select_related("offering")
        .prefetch_related("teaching")
    }

    teaches = (
        LessonOccurrenceTeach.objects.filter(
            lesson_occurrence__course_id__in=courses.keys()
        )
        .select_related("teacher", "lesson_occurrence")
        .order_by(
            "teacher__first_name",
            "teacher__last_name",
            "teacher_id",
            "lesson_occurrence__course__offering_id",
            "lesson_occurrence__course__name",
            "lesson_occurrence__course_id",
            "lesson_occurrence__start",
        )
    )

    teaches_by_teacher: dict[User, dict[Course, list[LessonOccurrenceTeach]]] = {}
    for teach in teaches:
        course = courses[teach.lesson_occurrence.course_id]
        teaches_by_teacher.setdefault(teach.teacher, {}).setdefault(course, []).append(
            teach
        )
    return teaches_by_teacher


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
        .prefetch_related("profile__address", "profile__bank_account")
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
