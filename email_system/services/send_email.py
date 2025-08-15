import logging
from typing import Iterable, Optional, Union

from django.core.exceptions import ValidationError
from post_office import mail
from post_office.models import Email, EmailTemplate

from tq_website import settings

log = logging.getLogger("tq")

HEADER_REPLY_TO = "Reply-To"

def send_email(
    to: Union[str, Iterable[str]],
    reply_to: Optional[str] = None,
    template: Optional[str] = None,
    context: Optional[dict] = None,
    sender: Optional[str] = None,
    subject: Optional[str] = None,
    headers: Optional[dict] = None,
    message: Optional[str] = None,
    html_message: Optional[str] = None,
    attachments: Optional[dict] = None,
) -> Optional[Email]:
    # https://stackoverflow.com/questions/26320899/why-is-the-empty-dictionary-a-dangerous-default-value-in-python
    if headers is None:
        headers =  dict()

    if reply_to:
        headers[HEADER_REPLY_TO] = reply_to
    elif HEADER_REPLY_TO not in headers:
         headers[HEADER_REPLY_TO] = settings.EMAIL_ADDRESS_CONTACT

    email = dict(
        recipients=to if isinstance(to, list) else [to],
        template=template,
        context=context,
        sender=sender or settings.DEFAULT_FROM_EMAIL,
        subject=subject,
        headers=headers,
        message=message,
        html_message=html_message,
        attachments=attachments,
    )

    try:
        return mail.send(**email)

    except ValidationError as e:
        log.warning(f"Validation failed: {repr(e)}. Data: {email}")
    except EmailTemplate.DoesNotExist:
        log.error(f"Email Template missing with name: {email['template']}")

    return None
