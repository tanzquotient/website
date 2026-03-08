from django.conf import settings
from django.utils import timezone
from django.urls import reverse
import logging
from datetime import datetime, time, timedelta

from post_office.models import EmailTemplate

from courses.models import Attendance, AttendanceState
from email_system.services import send_all_emails
from utils import TranslationUtils

log = logging.getLogger("tq")


def send_unexcused_absences_emails() -> None:
    try:
        email_template = EmailTemplate.objects.get(name="unexcused_absence")
    except EmailTemplate.DoesNotExist:
        log.error("EmailTemplate 'unexcused_absence' not found; aborting send")
        return

    emails = []

    # determine previous calendar day in local timezone
    local_now = timezone.localtime(timezone.now())
    previous_date = (local_now - timedelta(days=1)).date()
    tz = timezone.get_current_timezone()
    start_of_prev = timezone.make_aware(datetime.combine(previous_date, time.min), tz)
    start_of_next = timezone.make_aware(
        datetime.combine(previous_date + timedelta(days=1), time.min), tz
    )

    attendances = Attendance.objects.filter(
        state=AttendanceState.ABSENT_NOT_EXCUSED,
        lesson_occurrence__start__gte=start_of_prev,
        lesson_occurrence__start__lt=start_of_next,
    ).select_related("user", "lesson_occurrence__course")

    for attendance in attendances:
        user = attendance.users
        occ = attendance.lesson_occurrence
        course = occ.course
        start = occ.start
        course_type = course.type
        course_name_en = (
            course_type.safe_translation_getter("title", language_code="en") or ""
        )
        course_name_de = (
            course_type.safe_translation_getter("title", language_code="de") or ""
        )
        date_str = timezone.localtime(start).strftime("%d.%m.%Y")
        my_courses_url = (
            f"https://{settings.DEPLOYMENT_DOMAIN}{reverse('user_courses')}"
        )

        context = {
            "first_name": user.first_name,
            "course_name_en": course_name_en,
            "course_name_de": course_name_de,
            "date": date_str,
            "my_courses_url": my_courses_url,
        }

        emails.append(
            dict(
                to=user.email,
                reply_to=getattr(settings, "EMAIL_ADDRESS_COURSE_SUBSCRIPTIONS", None),
                template=email_template,
                context=context,
            )
        )

    log.info(f"Sending {len(emails)} unexcused absence emails")
    if emails:
        send_all_emails(emails)
