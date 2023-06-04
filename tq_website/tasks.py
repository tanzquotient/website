from celery import shared_task
from django.conf import settings
from post_office.mail import send_queued

from groups.services import update_groups
from payment.payment_processor import PaymentProcessor
from payment.postfinance_connector import FDSConnection
from payment.parser import ISO2022Parser, ZkbCsvParser


@shared_task(
    name="post_office_send_queued_emails",
    ignore_result=True,
    **settings.CELERY_EMAIL_TASK_CONFIG
)
def send_queued_emails() -> None:
    send_queued()


@shared_task(name="payment_get_fds_files", ignore_result=True)
def get_fds_files() -> None:
    fds_connector = FDSConnection()
    fds_connector.get_files()


@shared_task(name="payment_parse_fds_files", ignore_result=True)
def parse_iso_20022_files() -> None:
    ISO2022Parser.parse_files_and_save_payments()


@shared_task(name="payment_parse_zkb_csv_files", ignore_result=True)
def payment_parse_zkb_csv_files() -> None:
    ZkbCsvParser.parse_files_and_save_payments()


@shared_task(name="payment_match", ignore_result=True)
def match_payments() -> None:
    PaymentProcessor().process_payments()


@shared_task(name="update_groups", ignore_result=True)
def task_update_groups() -> None:
    update_groups()
