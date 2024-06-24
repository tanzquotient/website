from datetime import date, timedelta
import logging

from django.contrib import messages
from django.utils.translation import gettext as _

from courses import models as models
from courses.models import choices as choices
from courses.emailcenter import send_teacher_welcome

from tq_website import settings
from email_system.services import send_all_emails

log = logging.getLogger("tq")


def welcome_teacher(teach):
    if not teach.welcomed:
        teach.welcomed = True
        teach.save()

        m = send_teacher_welcome(teach)
        if m:
            # log that we sent the confirmation
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
        _("{} of {} welcomed successfully").format(count, total),
    )


def welcome_teachers_reset_flag(courses, request):
    count = 0
    total = 0
    for course in courses:
        for teach in course.teaching.all():
            if teach.welcomed:
                count += 1
                teach.welcomed = False
                teach.save()
            total += 1
    messages.add_message(
        request,
        messages.SUCCESS,
        _("{} of {} teachers reset successfully").format(count, total),
    )


def send_presence_reminder() -> None:

    # look for courses that ended yesterday
    courses: list[models.Course] = list(
        models.Course.objects.exclude(cancelled=True)
        .exclude(subscription_type=choices.CourseSubscriptionType.EXTERNAL)
        .all()
    )
    courses_yesterday = [
        course
        for course in courses
        if course.get_last_lesson_date() == date.today() - timedelta(days=1)
    ]

    # look for courses that ended 7 days ago and for which some lesson occurrence
    # is lacking presence data
    courses_last_week = [
        course
        for course in courses
        if (course.get_last_lesson_date() == date.today() - timedelta(days=7))
        and course.lesson_occurrences.filter(teachers=None).exists()
    ]

    courses = courses_yesterday + courses_last_week

    emails = []

    for course in courses:
        main_teachers = course.get_teachers()
        for main_teacher in main_teachers:
            context = {
                "first_name": main_teacher.first_name,
                "course": course.type.name,
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
