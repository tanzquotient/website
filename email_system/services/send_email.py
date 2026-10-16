import logging
from collections.abc import Iterable

from django.core.exceptions import ValidationError
from post_office import mail
from post_office.models import Email, EmailTemplate

from tq_website import settings

log = logging.getLogger("tq")

HEADER_REPLY_TO = "Reply-To"


def send_email(
    to: str | Iterable[str],
    reply_to: str | None = None,
    template: str | None = None,
    context: dict | None = None,
    sender: str | None = None,
    subject: str | None = None,
    headers: dict | None = None,
    message: str | None = None,
    html_message: str | None = None,
    attachments: dict | None = None,
) -> Email | None:
    # https://stackoverflow.com/questions/26320899/why-is-the-empty-dictionary-a-dangerous-default-value-in-python
    if headers is None:
        headers = {}

    if reply_to:
        headers[HEADER_REPLY_TO] = reply_to
    elif HEADER_REPLY_TO not in headers:
        headers[HEADER_REPLY_TO] = settings.EMAIL_ADDRESS_CONTACT

    email = {
        "recipients": to if isinstance(to, list) else [to],
        "template": template,
        "context": context,
        "sender": sender or settings.DEFAULT_FROM_EMAIL,
        "subject": subject,
        "headers": headers,
        "message": message,
        "html_message": html_message,
        "attachments": attachments,
    }

    try:
        return mail.send(**email)

    except ValidationError as e:
        log.warning(f"Validation failed: {e!r}. Data: {email}")
    except EmailTemplate.DoesNotExist:
        log.error(f"Email Template missing with name: {email['template']}")

    return None
