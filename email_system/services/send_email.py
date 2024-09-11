import logging
from typing import Iterable, Optional, Union

from django.core.exceptions import ValidationError
from post_office import mail
from post_office.models import Email, EmailTemplate

from email_system.services.tq_email_templates import TqEmailTemplate
from tq_website import settings

log = logging.getLogger("tq")


def send_email(
    to: Union[str, Iterable[str]],
    reply_to: Optional[str] = None,
    template_db: Optional[str] = None,
    template_tq: Optional[TqEmailTemplate] = None,
    context: Optional[dict] = None,
    sender: Optional[str] = None,
    subject: Optional[str] = None,
    headers: Optional[dict] = None,
    message: Optional[str] = None,
    html_message: Optional[str] = None,
    attachments: Optional[dict] = None,
) -> Optional[Email]:
    """
    Send an email using PostOffice.

    Possible options (in order of precedence):

    1. Use an email template stored in git.
    Subject, message, html_message are ignored.

    2. Use an email template stored in the database
    (https://tanzquotient.org/admin/post_office/emailtemplate/).
    Subject, message, html_message are ignored.

    3. Manually provide subject, message, html_message.
    """
    if template_tq:
        subject, message, html_message = template_tq.render(context)

        if template_db:
            log.warning(
                f"Ignoring template_db={template_db} because template_tq={template_tq} is set."
            )
            template_db = None

    email = dict(
        recipients=to if isinstance(to, list) else [to],
        template=template_db,
        context=context,
        sender=sender or settings.DEFAULT_FROM_EMAIL,
        subject=subject,
        headers=headers
        or {
            "Reply-to": reply_to or settings.EMAIL_ADDRESS_CONTACT,
        },
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
