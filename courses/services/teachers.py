from django.contrib import messages
from django.utils.translation import gettext as _

from courses import models as models
from courses.emailcenter import send_teacher_welcome


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
