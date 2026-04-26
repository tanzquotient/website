from datetime import date, timedelta
import logging

from django.contrib import messages
from django.utils.translation import gettext as _
from django.urls import reverse

from courses import models as models
from courses.models import choices as choices
from courses.emailcenter import send_teacher_welcome

from tq_website import settings
from email_system.services import send_all_emails

log = logging.getLogger("tq")


def welcome_teacher(teach):
    if not teach.welcomed:
        m = send_teacher_welcome(teach)
        if m:
            # log that we enqueued/sent the confirmation; TeacherWelcome records the mail
            c = models.TeacherWelcome(teach=teach, mail=m)
            c.save()
            return True
        else:
            return False
    else:
        return False


def welcome_teachers(courses, request):
    count = 0
    total = 0
    for course in courses:
        for teach in course.teaching.all():
            total += 1
            if welcome_teacher(teach):
                count += 1
    messages.add_message(
        request,
        messages.SUCCESS,
        _(
            "{} of {} welcome emails dispatched. Please allow "
            "a few minutes for all emails to be sent."
        ).format(count, total),
    )


def send_presence_reminder() -> None:
    yesterday = date.today() - timedelta(days=1)
    last_week = date.today() - timedelta(days=7)

    courses_yesterday = []
    courses_last_week = []

    course_qs = (
        models.Course.objects.exclude(cancelled=True)
        .exclude(subscription_type=choices.CourseSubscriptionType.EXTERNAL)
    )
    for course in course_qs.iterator(chunk_size=200):
        last_lesson = course.get_last_lesson_date()
        if last_lesson == yesterday:
            courses_yesterday.append(course)
        elif (
            last_lesson == last_week
            and course.lesson_occurrences.filter(teachers=None).exists()
        ):
            courses_last_week.append(course)

    courses = courses_yesterday + courses_last_week

    emails = []

    for course in courses:
        main_teachers = course.get_teachers()
        for main_teacher in main_teachers:
            context = {
                "first_name": main_teacher.first_name,
                "course": course.type.title,
                "teacher_presence_url": (
                    "https://"
                    + settings.DEPLOYMENT_DOMAIN
                    + reverse(
                        "payment:course_teacher_presence", kwargs={"course": course.id}
                    )
                ),
            }
            log.info(
                f"Will send presence form reminder to {main_teacher.username} for course {course.type.title} in offering {course.offering.name}"
            )

            emails.append(
                dict(
                    to=main_teacher.email,
                    reply_to=settings.EMAIL_ADDRESS_DANCE_ADMIN,
                    template="teacher_course_presence_reminder",
                    context=context,
                )
            )

    log.info(f"Sending {len(emails)} emails")
    send_all_emails(emails)
