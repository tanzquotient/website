import math
from collections.abc import Iterable
from datetime import datetime
from typing import Any

import reversion
from django.contrib.auth.models import User
from post_office.models import EmailTemplate

from courses.models import Course, CourseType, Voucher
from courses.services.general import log
from email_system.services import send_all_emails
from survey.models import Survey, SurveyInstance
from tq_website import settings


def get_next_level_type(course_type: CourseType) -> CourseType | None:
    """
    Returns the successor of the course type (as set for early sign-up) one level
    higher, the course type itself if it is its own successor (e.g. a show group)
    or None if there is no unique successor.
    """
    successors = list(course_type.successors.all())
    candidates = []
    if course_type.level is not None:
        candidates = [t for t in successors if t.level == course_type.level + 1]
    if len(candidates) > 1:
        # e.g. Bachata 3 and Bachata Sensual 3 for Bachata 2
        next_title = course_type.title.replace(
            str(course_type.level), str(course_type.level + 1)
        )
        candidates = [t for t in candidates if t.title == next_title]
    if len(candidates) == 1:
        return candidates[0]
    return course_type if course_type in successors else None


def get_copy_notes(course: Course) -> list[str]:
    """Describes what Course.copy() changes or leaves out for the given course."""
    notes = []
    if course.cancelled:
        notes.append("Cancelled, offered again at the same level")
    if course.period:
        notes.append(f"Custom period {course.period} replaced by the offering period")
    irregular_lessons = course.irregular_lessons.all()
    if not course.regular_lessons.all():
        notes.append("No regular lessons, add the lessons manually")
    if irregular_lessons:
        notes.append(f"{len(irregular_lessons)} irregular lesson(s) not copied")
    return notes


def send_course_email(data: dict[str, Any], courses: Iterable[Course]) -> None:
    email_template: EmailTemplate | None = data["email_template"]
    email_subject: str | None = data["email_subject"]
    email_content: str | None = data["email_content"]
    send_to_participants: bool = data["send_to_participants"]
    send_to_teachers: bool = data["send_to_teachers"]
    survey: Survey | None = data["survey"]
    survey_url_expire_date: datetime | None = data["survey_url_expire_date"]

    emails = []

    for course in courses:
        recipients: list[User] = []
        if send_to_participants:
            subscribes = course.subscriptions.filter(
                state__in=data["subscribe_state"]
            ).all()
            recipients += [s.user for s in subscribes]
        if send_to_teachers:
            recipients += course.get_teachers()

        for recipient in recipients:
            # Get context for email
            context = {
                "first_name": recipient.first_name,
                "last_name": recipient.last_name,
                "course": course.type.title,
                "offering": course.offering.name,
                "offering_title_en": course.offering.safe_translation_getter(
                    "title", language_code="en"
                ),
                "offering_title_de": course.offering.safe_translation_getter(
                    "title", language_code="de"
                ),
            }

            if survey:
                survey_instance = SurveyInstance.objects.create(
                    survey=survey,
                    email_template=email_template,
                    course=course,
                    user=recipient,
                    url_expire_date=survey_url_expire_date,
                )
                context["survey_url"] = survey_instance.create_full_url()
                context["survey_expiration"] = survey_instance.url_expire_date

            subject: str = email_subject
            message: str | None = None
            html_message: str | None = email_content

            if email_template:
                subject = subject or email_template.subject
                message = message or email_template.content
                html_message = html_message or email_template.html_content

            emails.append(
                {
                    "to": recipient.email,
                    "reply_to": settings.EMAIL_ADDRESS_COURSE_SUBSCRIPTIONS,
                    "subject": subject,
                    "message": message,
                    "html_message": html_message,
                    "context": context,
                }
            )

    log.info(f"Sending {len(emails)} emails")
    send_all_emails(emails)


def create_send_vouchers(data, subscriptions, user):
    percentage = data.get("percentage")
    amount = data.get("amount")
    purpose = data["purpose"]
    expires_flag = data["expires_flag"]
    expires = data["expires"]
    voucher_comment = data["voucher_comment"]

    vouchers_to_send = []

    for subscription in subscriptions:
        recipient = subscription.user
        voucher_amount = (
            math.ceil(percentage * subscription.get_price_to_pay() / 100)
            if percentage
            else amount
        )
        with reversion.create_revision():
            voucher = Voucher.objects.create(
                purpose=purpose,
                amount=voucher_amount,
                expires=expires if expires_flag else None,
                sent_to=recipient,
                comment=voucher_comment,
            )
            reversion.set_user(user)
            reversion.set_comment(f"Sent voucher email to {recipient}")

        vouchers_to_send.append(voucher)

    email_vouchers(data=data, vouchers=vouchers_to_send)


def email_vouchers(data: dict, vouchers: list[Voucher]):
    custom_msg_en = data["custom_email_message_en"] or ""
    custom_msg_de = data["custom_email_message_de"] or ""

    emails = []

    for voucher in vouchers:
        email_context = {
            "first_name": voucher.sent_to.first_name,
            "last_name": voucher.sent_to.last_name,
            "voucher_key": voucher.key,
            "voucher_url": voucher.pdf_file.url,
            "custom_msg_en": custom_msg_en,
            "custom_msg_de": custom_msg_de,
            "voucher_expires": voucher.expires,
        }

        emails.append(
            {
                "to": voucher.sent_to.email,
                "reply_to": settings.EMAIL_ADDRESS_COURSE_SUBSCRIPTIONS,
                "template": "voucher",
                "context": email_context,
                "attachments": {"Voucher.pdf": voucher.pdf_file.file},
            }
        )

    log.info(f"Sending {len(emails)} emails")
    send_all_emails(emails)
