from celery import shared_task
from django.conf import settings
from post_office.mail import send_queued_mail_until_done

from groups.services import update_groups
from survey.services import send_course_surveys
from payment.payment_processor import PaymentProcessor
from payment.parser import ZkbCsvParser
from courses.services.teachers import send_presence_reminder
from email_system.services import send_scheduled_group_emails
from photologue.models import ImageModel, PhotoSizeCache


@shared_task(
    name="post_office_send_queued_emails",
    ignore_result=True,
    **settings.CELERY_EMAIL_TASK_CONFIG
)
def send_queued_emails() -> None:
    send_queued_mail_until_done()


@shared_task(name="payment_parse_zkb_csv_files", ignore_result=True)
def payment_parse_zkb_csv_files() -> None:
    ZkbCsvParser.parse_files_and_save_payments()


@shared_task(name="payment_match", ignore_result=True)
def match_payments() -> None:
    PaymentProcessor().process_payments()


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
    for image in ImageModel.objects.all():
        for photosize in PhotoSizeCache().sizes.values():
            image.create_size(photosize, recreate=False)
