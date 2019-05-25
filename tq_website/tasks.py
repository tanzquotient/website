from django.conf import settings

from courses.admin_actions import update_dance_teacher_group

try:
    from celery import shared_task
except ImportError:
    from celery.decorators import task as shared_task

# Make sure our AppConf is loaded properly.

from post_office.mail import send_queued
from payment.postfinance_connector import FDSConnection, ISO2022Parser
from payment.payment_processor import PaymentProcessor

# Messages *must* be dicts, not instances of the EmailMessage class
# This is because we expect Celery to use JSON encoding, and we want to prevent
# code assuming otherwise.

TASK_CONFIG_EMAILS = {'name': 'post_office_send_queued_emails', 'ignore_result': True}
TASK_CONFIG_EMAILS.update(settings.CELERY_EMAIL_TASK_CONFIG)

@shared_task(**TASK_CONFIG_EMAILS)
def send_queued_emails():
    return send_queued()


TASK_CONFIG_FDS = {'name': 'payment_get_fds_files', 'ignore_result': True}

@shared_task(**TASK_CONFIG_FDS)
def get_fds_files():
    fds_connector = FDSConnection()
    return fds_connector.get_files()

TASK_CONFIG_PARSE = {'name': 'payment_parse_fds_files', 'ignore_result': True}

@shared_task(**TASK_CONFIG_PARSE)
def parse_iso_20022_files():
    parser = ISO2022Parser()
    return parser.parse()


TASK_CONFIG_MATCH = {'name': 'payment_match', 'ignore_result': True}

@shared_task(**TASK_CONFIG_MATCH)
def match_payments():
    PaymentProcessor().process_payments()


TASK_CONFIG_TEACHER_GROUP = {'name': 'update_teacher_group', 'ignore_result': True}

@shared_task(**TASK_CONFIG_TEACHER_GROUP)
def update_teacher_group():
    update_dance_teacher_group()