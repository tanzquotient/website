import logging
from collections.abc import Iterable

from post_office.models import Email

from .send_email import send_email

log = logging.getLogger("tq")


def send_all_emails(emails: Iterable[dict]) -> list[Email]:
    sent_emails = []
    for email in emails:
        sent_email = send_email(**email)
        if sent_email:
            sent_emails.append(sent_email)

    return sent_emails
