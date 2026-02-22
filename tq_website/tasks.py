from celery import shared_task
from django.core.cache import cache

from groups.services import update_groups
from survey.services import send_course_surveys
from payment.payment_processor import PaymentProcessor
from payment.parser import ZkbCsvParser
from payment.services import remind_all_of_payments
from courses.services.teachers import send_presence_reminder
from email_system.services import send_scheduled_group_emails, send_queued_emails
from photologue.models import Photo, PhotoSizeCache
from courses.models import Course, Subscribe, CourseType, Teach, LessonOccurrence


@shared_task(
    name="custom_post_office_send_queued_emails",
    ignores_result=True,
)
def custom_send_queued_emails() -> None:
    send_queued_emails()


@shared_task(name="post_office.tasks.send_queued_mail", ignore_result=True)
def post_office_override_send_queued_emails() -> None:
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


@shared_task(name="delete_user_and_courses_calendar_cache", ignore_result=True)
def task_delete_user_and_courses_calendar_cache(
    pk: int,
    sender: str,
    **kwargs,
) -> None:
    users = set()
    courses = set()

    def _add_users_from_course(course: Course):
        users.update(course.subscriptions.all().values_list("user", flat=True))
        users.update(course.teaching.all().values_list("teacher", flat=True))

    if sender == Course.__name__:
        course = Course.objects.get(pk=pk)
        _add_users_from_course(course)
        courses.add(course.pk)
    elif sender == CourseType.__name__:
        course_type = CourseType.objects.get(pk=pk)
        courses_with_type = course_type.courses.all()
        for course in courses_with_type:
            courses.add(course.pk)
            _add_users_from_course(course)
    elif sender == Subscribe.__name__:
        subscribe = Subscribe.objects.get(pk=pk)
        users.add(subscribe.user.pk)
    elif sender == Teach.__name__:
        teach = Teach.objects.get(pk=pk)
        _add_users_from_course(teach.course)
        courses.add(teach.course.pk)
    elif sender == LessonOccurrence.__name__:
        lesson_occurrence = LessonOccurrence.objects.get(pk=pk)
        _add_users_from_course(lesson_occurrence.course)
        courses.add(lesson_occurrence.course.pk)

    for user in users:
        cache_key = f"user_ical_{user}"
        cache.delete(cache_key)

    for course in courses:
        cache_key = f"course_ical_{course}"
        cache.delete(cache_key)
