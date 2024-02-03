import logging
from typing import Iterable

from post_office.models import Email
from celery import shared_task

from . import send_email

log = logging.getLogger("tq")

def send_all_emails(emails: Iterable[dict]) -> list[Email]:
    sent_emails = [send_single_email_task.delay(email) for email in emails]
    return [result.get() for result in sent_emails]

@shared_task(name="send_single_email_task")
def send_single_email_task(email: dict) -> Email:
    return send_email(**email)
