from django.conf import settings
from django.core.mail import EmailMessage, get_connection

try:
    from celery import shared_task
except ImportError:
    from celery.decorators import task as shared_task

# Make sure our AppConf is loaded properly.
import djcelery_email.conf  # noqa

from post_office.mail import send_queued
from payment.postfinance_connector import FDSConnection, ISO2022Parser

# Messages *must* be dicts, not instances of the EmailMessage class
# This is because we expect Celery to use JSON encoding, and we want to prevent
# code assuming otherwise.

TASK_CONFIG = {'name': 'post_office_send_queued_emails', 'ignore_result': True}
TASK_CONFIG.update(settings.CELERY_EMAIL_TASK_CONFIG)


@shared_task(**TASK_CONFIG)
def send_queued_emails():
    return send_queued()

@shared_task(**TASK_CONFIG)
def get_fds_files():
    fds_connector = FDSConnection()
    return fds_connector.get_files()

@shared_task(**TASK_CONFIG)
def parse_iso_20022_files():
    parser = ISO2022Parser()
    return parser.parse()