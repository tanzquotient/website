import logging
from datetime import date, timedelta

from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import override
from post_office.models import EmailTemplate

from courses.models import UserProfile
from email_system.services import send_all_emails

log = logging.getLogger("tq")

STUDENT_STATUS_EXPIRY_NOTICE_DAYS = 30


def send_student_status_expiring_emails() -> None:
    """Remind users whose student status expires in 30 days to renew it."""
    _send_student_status_emails(
        template_name="student_status_expiring",
        student_validity=timezone.localdate()
        + timedelta(days=STUDENT_STATUS_EXPIRY_NOTICE_DAYS),
    )


def send_student_status_expired_emails() -> None:
    """Tell users whose student status expired yesterday that they can renew it."""
    _send_student_status_emails(
        template_name="student_status_expired",
        student_validity=timezone.localdate() - timedelta(days=1),
    )


def _send_student_status_emails(template_name: str, student_validity: date) -> None:
    try:
        email_template = EmailTemplate.objects.get(name=template_name)
    except EmailTemplate.DoesNotExist:
        log.error(f"EmailTemplate '{template_name}' not found; aborting send")
        return

    # Only the Switch edu-ID student status uses student_validity, and it can only be
    # renewed with a linked edu-ID.
    profiles = UserProfile.objects.filter(
        student_validity=student_validity,
        switch_data__isnull=False,
        user__is_active=True,
        # TODO: remove together with the is_staff conditional in UserProfile.is_student
        user__is_staff=True,
    ).select_related("user")

    with override("de"):
        profile_url_de = f"https://{settings.DEPLOYMENT_DOMAIN}{reverse('profile')}"
    with override("en"):
        profile_url_en = f"https://{settings.DEPLOYMENT_DOMAIN}{reverse('profile')}"

    emails = [
        dict(
            to=profile.user.email,
            reply_to=settings.EMAIL_ADDRESS_COURSE_SUBSCRIPTIONS,
            template=email_template,
            context={
                "first_name": profile.user.first_name,
                "valid_until": student_validity.strftime("%d.%m.%Y"),
                "profile_url_de": profile_url_de,
                "profile_url_en": profile_url_en,
            },
        )
        for profile in profiles
        if profile.user.email
    ]

    log.info(f"Sending {len(emails)} '{template_name}' emails")
    if emails:
        send_all_emails(emails)
