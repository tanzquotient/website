from django.core.exceptions import ValidationError
from post_office import mail


def send_all_emails(emails):
    sent_emails = list()
    for email in emails:
        try:
            # Send email
            email = mail.send(**email)
            sent_emails.append(email)

        # Invalid email address
        except ValidationError:
            pass

    return sent_emails