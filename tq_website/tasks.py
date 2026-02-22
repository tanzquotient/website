from celery import shared_task
from django.conf import settings
from post_office.mail import send_queued_mail_until_done
from django.test.client import RequestFactory
from django.utils.cache import get_cache_key
from django.core.cache import cache
from django.urls import reverse

from groups.services import update_groups
from survey.services import send_course_surveys
from payment.payment_processor import PaymentProcessor
from payment.parser import ZkbCsvParser
from payment.services import remind_all_of_payments
from courses.services.teachers import send_presence_reminder
from email_system.services import send_scheduled_group_emails, send_queued_emails
from photologue.models import Photo, PhotoSizeCache
from courses.models import Course, Subscribe, CourseType, Teach, LessonOccurrence
from courses.views import _user_specific_token


@shared_task(
    name="custom_post_office_send_queued_emails",
    ignores_result=True,
)
@shared_task(name="post_office.tasks.send_queued_mail", ignore_result=True)
def custom_send_queued_emails() -> None:
    send_queued_emails()


@shared_task(name="payment_parse_zkb_csv_files", ignore_result=True)
def payment_parse_zkb_csv_files() -> None:
    ZkbCsvParser.parse_files_and_save_payments()


@shared_task(name="payment_match", ignore_result=True)
def match_payments(send_reminders: bool = False) -> None:
    PaymentProcessor().process_payments()
    if send_reminders:
        remind_all_of_payments(
            min_days_from_course_start=14, min_days_from_previous_reminder=7
        )


@shared_task(name="update_groups", ignore_result=True)
def task_update_groups() -> None:
    update_groups()


@shared_task(name="send_course_surveys", ignore_result=True)
def task_send_course_surveys() -> None:
    send_course_surveys()


@shared_task(name="send_course_presence_reminder", ignore_result=True)
def task_send_course_presence_reminder() -> None:
    send_presence_reminder()


@shared_task(name="send_scheduled_group_emails", ignore_result=True)
def task_send_scheduled_group_emails() -> None:
    send_scheduled_group_emails()


@shared_task(name="pre_cache_photologue_image_sizes", ignore_result=True)
def task_pre_cache_photologue_image_sizes() -> None:
    for image in Photo.objects.all():
        for photosize in PhotoSizeCache().sizes.values():
            image.create_size(photosize, recreate=False)


@shared_task(name="delete_user_calendar_cache", ignore_result=True)
def task_delete_user_and_courses_calendar_cache(
    pk,
    sender,
    **kwargs,
) -> None:
    users = set()
    courses = set()

    def _add_users_from_course(course: Course):
        users.update(course.subscriptions.all().values_list("user", flat=True))
        users.update(course.teaching.all().values_list("teacher", flat=True))

    if sender == Course:
        course = Course.objects.get(pk=pk)
        _add_users_from_course(course)
        courses.add(course)
    elif sender == CourseType:
        course_type = CourseType.objects.get(pk=pk)
        courses_with_type = course_type.courses.all()
        for course in courses_with_type:
            courses.add(course)
            _add_users_from_course(course)
    elif sender == Subscribe:
        subscribe = Subscribe.objects.get(pk=pk)
        users.add(subscribe.user)
    elif sender == Teach:
        teach = Teach.objects.get(pk=pk)
        _add_users_from_course(teach.course)
        courses.add(teach.course)
    elif sender == LessonOccurrence:
        lesson_occurrence = LessonOccurrence.objects.get(pk=pk)
        _add_users_from_course(lesson_occurrence.course)
        courses.add(lesson_occurrence.course)

    for user in users:
        req = RequestFactory().get(
            reverse("user_ical", kwargs={"user_id": user.pk}),
            {"token": _user_specific_token(user)},
        )
        key = get_cache_key(req)
        cache.delete(key)

    for course in courses:
        req = RequestFactory().get(
            reverse("course_ical", kwargs={"course_id": course.pk}),
        )
        key = get_cache_key(req)
        cache.delete(key)
