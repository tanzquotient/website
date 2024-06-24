from datetime import datetime
from typing import Iterable, Any, Optional

import reversion
from django.contrib.auth.models import User
from post_office.models import EmailTemplate

from courses import models as models
from courses.models import Voucher, Course
from courses.services import get_subsequent_offering
from courses.services.general import log
from email_system.services import send_all_emails
from payment.utils.generate_voucher_pdf import generate_voucher_pdfs
from survey.models import SurveyInstance, Survey
from tq_website import settings


def copy_course(course, to=None):
    if to is None:
        to = get_subsequent_offering()
    if to is not None:
        course_copy = course.copy()
        course_copy.offering = to
        course_copy.active = False
        course_copy.save()


def send_course_email(data: dict[str, Any], courses: Iterable[Course]) -> None:
    email_template: Optional[EmailTemplate] = data["email_template"]
    email_subject: Optional[str] = data["email_subject"]
    email_content: Optional[str] = data["email_content"]
    send_to_participants: bool = data["send_to_participants"]
    send_to_teachers: bool = data["send_to_teachers"]
    survey: Optional[Survey] = data["survey"]
    survey_url_expire_date: Optional[datetime] = data["survey_url_expire_date"]

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
            message: Optional[str] = None
            html_message: Optional[str] = email_content

            if email_template:
                subject = subject or email_template.subject
                message = message or email_template.content
                html_message = html_message or email_template.html_content

            emails.append(
                dict(
                    to=recipient.email,
                    reply_to=settings.EMAIL_ADDRESS_DANCE_ADMIN,
                    subject=subject,
                    message=message,
                    html_message=html_message,
                    context=context,
                )
            )

    log.info("Sending {} emails".format(len(emails)))
    send_all_emails(emails)


def create_send_vouchers(data, recipients, user):
    amount = data["amount"]
    percentage = data["percentage"]
    purpose = data["purpose"]
    expires_flag = data["expires_flag"]
    expires = data["expires"]
    voucher_comment = data["voucher_comment"]

    vouchers_to_send = []

    for recipient in recipients:
        with reversion.create_revision():
            voucher = Voucher.objects.create(
                purpose=purpose,
                percentage=percentage,
                amount=amount,
                expires=expires if expires_flag else None,
                sent_to=recipient,
                comment=voucher_comment,
            )
            reversion.set_user(user)
            reversion.set_comment(f"Sent voucher email to {recipient}")

        generate_voucher_pdfs(vouchers=[voucher])

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
        }

        emails.append(
            dict(
                to=voucher.sent_to.email,
                template="voucher",
                context=email_context,
                attachments={"Voucher.pdf": voucher.pdf_file.file},
            )
        )

    log.info("Sending {} emails".format(len(emails)))
    send_all_emails(emails)
