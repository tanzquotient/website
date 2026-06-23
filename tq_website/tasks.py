from celery import shared_task
from django.core.cache import cache
from photologue.models import Photo, PhotoSizeCache

from courses.services.attendance import send_unexcused_absences_emails
from courses.services.teachers import send_presence_reminder
from email_system.services import send_queued_emails, send_scheduled_group_emails
from groups.services import update_groups
from payment.parser import ZkbCsvParser
from payment.payment_processor import PaymentProcessor
from payment.services import remind_all_of_payments
from survey.services import send_course_surveys


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


@shared_task(name="send_unexcused_absences_emails", ignore_result=True)
def task_send_unexcused_absences_emails() -> None:
    send_unexcused_absences_emails()


@shared_task(name="send_course_presence_reminder", ignore_result=True)
def task_send_course_presence_reminder() -> None:
    send_presence_reminder()


@shared_task(name="send_scheduled_group_emails", ignore_result=True)
def task_send_scheduled_group_emails() -> None:
    send_scheduled_group_emails()


@shared_task(name="pre_cache_photologue_image_sizes", ignore_result=True)
def task_pre_cache_photologue_image_sizes() -> None:
    photosizes = list(PhotoSizeCache().sizes.values())
    for image in Photo.objects.iterator(chunk_size=50):
        for photosize in photosizes:
            image.create_size(photosize, recreate=False)


@shared_task(name="delete_user_and_courses_calendar_cache", ignore_result=True)
def task_delete_user_and_courses_calendar_cache(
    user_ids: list[int],
    course_ids: list[int],
) -> None:
    for user_id in user_ids:
        cache.delete(f"user_ical_{user_id}")
    for course_id in course_ids:
        cache.delete(f"course_ical_{course_id}")
