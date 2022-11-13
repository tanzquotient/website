from decimal import Decimal
from typing import Sequence

from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from courses.models import Offering, Teach, CourseSubscriptionType


def offering_finance_teachers(offerings: Sequence[Offering]) -> tuple[str, list, list]:
    """Exports a summary of the given ``offering`` concerning payment of teachers.

    Contains profile data relevant for payment of teachers and how many lesson at what rate to be paid.

    :param export_format: export format
    :param offerings: offerings to include in summary
    :return: response or ``None`` if format not supported
    """
    export_name = f'Salaries - {(offerings[0].name if len(offerings) == 1 else "Multiple Offerings")}'

    courses = _courses(offerings)
    personal_details = _personal_details(offerings)

    return export_name, personal_details, courses


def _courses(offerings: Sequence[Offering]) -> list:
    courses = []

    header = [
        _('Last name'),
        _('First name'),
        _('Courses'),
        _('Hourly Wages'),
        _('Hours'),
        _('Course Totals'),
        _('Note'),
        _('Teacher Total'),
    ]
    multiple_offerings = len(offerings) > 1
    if multiple_offerings:
        header += ['Offering']
    courses.append(header)

    teachings = Teach.objects \
        .filter(course__offering__in=offerings) \
        .exclude(course__subscription_type=CourseSubscriptionType.EXTERNAL)\
        .order_by('teacher__first_name', 'teacher__last_name', 'course__offering_id', 'course__name') \
        .all()

    last_teacher = None
    row = []
    teacher_total = 0
    for idx, teaching in enumerate(teachings):
        teacher = teaching.teacher
        course = teaching.course

        course_data = []

        has_participants = course.get_confirmed_count() > 0
        hours = Decimal(course.get_total_time()['total']) if has_participants else 0
        total = teaching.hourly_wage * hours

        if multiple_offerings:
            course_data.append(course.offering or "")

        course_data += [
            course.name,
            f"{teaching.hourly_wage} CHF",
            f"{hours}",
            f"{total:.2f} CHF",
            _('No participants') if not has_participants else "\u00A0",
        ]

        if teacher != last_teacher:
            teacher_total = total

            row = [
                teacher.first_name or "",
                teacher.last_name or "",
            ] + course_data + [
                f"{teacher_total:.2f} CHF"
            ]

            courses.append(row)

        else:
            teacher_total += total
            row[-1] = f"{teacher_total:.2f} CHF"
            for idx, value in enumerate(course_data):
                row[idx + 2] = f"{row[idx + 2]}\n{value}"

        last_teacher = teacher

    return courses


def _personal_details(offerings: Sequence[Offering]) -> list:
    personal_details = []
    header = [_('Last name'), _('First name'), _('E-mail'), _('Phone'), _('Address')]
    header += ['Birthdate', 'Nationality', 'Residence Permit', 'AHV Number', 'IBAN', 'Bank']

    personal_details.append(header)

    teachers = User.objects \
        .filter(teaching_courses__course__offering__in=offerings) \
        .exclude(teaching_courses__course__subscription_type=CourseSubscriptionType.EXTERNAL) \
        .order_by('first_name', 'last_name') \
        .distinct()\
        .all()

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
            teacher.profile.ahv_number
        ]

        if teacher.profile.bank_account:
            row += [teacher.profile.bank_account.iban, teacher.profile.bank_account.bank_info_str()]
        else:
            row += [""] * 2

        personal_details.append(row)

    return personal_details
