"""
Email backend sending emails through the Microsoft Graph API with the ETH service account.

Messages are submitted in MIME format, so that headers (e.g. Reply-To, List-Unsubscribe),
HTML alternatives and attachments are sent exactly as Django generates them.
https://learn.microsoft.com/en-us/graph/outlook-send-mime-message
"""

import base64
import email.policy
import time
from email.utils import parseaddr

import requests
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

REQUEST_TIMEOUT = 30  # seconds


class MicrosoftGraphError(Exception):
    pass


class MicrosoftGraphEmailBackend(BaseEmailBackend):
    # Shared by all instances of a process, since post_office creates a new backend for every batch
    _access_token: str | None = None
    _access_token_expires_at: float = 0.0

    @classmethod
    def _get_access_token(cls) -> str:
        if cls._access_token and time.monotonic() < cls._access_token_expires_at:
            return cls._access_token

        response = requests.post(
            f"https://login.microsoftonline.com/{settings.EMAIL_GRAPH_TENANT_ID}/oauth2/v2.0/token",
            data={
                "grant_type": "client_credentials",
                "client_id": settings.EMAIL_GRAPH_CLIENT_ID,
                "client_secret": settings.EMAIL_GRAPH_CLIENT_SECRET,
                "scope": "https://graph.microsoft.com/.default",
            },
            timeout=REQUEST_TIMEOUT,
        )
        if response.status_code != 200:
            raise MicrosoftGraphError(
                f"Authentication failed ({response.status_code}): {response.text}"
            )
        result = response.json()
        cls._access_token = result["access_token"]
        # Renew the token one minute before it expires
        cls._access_token_expires_at = time.monotonic() + result["expires_in"] - 60
        return cls._access_token

    def send_messages(self, email_messages) -> int:
        sent_count = 0
        for email_message in email_messages:
            try:
                self._send(email_message)
            except Exception:
                if not self.fail_silently:
                    raise
            else:
                sent_count += 1

        return sent_count

    def _send(self, email_message) -> None:
        message = email_message.message(policy=email.policy.SMTP)
        if email_message.bcc:
            # Django leaves Bcc out of the headers, but Graph takes the recipients from them
            message["Bcc"] = ", ".join(email_message.bcc)

        # The service account's mailbox, which is the From address of all emails
        sender = parseaddr(settings.DEFAULT_FROM_EMAIL)[1]
        response = requests.post(
            f"https://graph.microsoft.com/v1.0/users/{sender}/sendMail",
            headers={
                "Authorization": f"Bearer {self._get_access_token()}",
                "Content-Type": "text/plain",
            },
            data=base64.b64encode(message.as_bytes()),
            timeout=REQUEST_TIMEOUT,
        )
        if response.status_code != 202:
            raise MicrosoftGraphError(
                f"Sending failed ({response.status_code}): {response.text}"
            )
