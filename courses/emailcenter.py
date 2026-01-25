import logging
from typing import Optional
from tempfile import TemporaryFile

from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from post_office.models import Email

import courses.models
from courses.models import Subscribe, Teach, Course, SubscribeState
from email_system.services import send_email
from payment.utils import create_qrbill_for_subscription, to_pdf
from payment import payment_processor

log = logging.getLogger("tq")


# Note: the email templates used for rendering are stored in the database.
# For convenience, the templates are also stored in git in the email_templates/ directory.
# See the email_templates/README.md for details.


def send_subscription_confirmation(subscription: Subscribe) -> Optional[Email]:
    context = {
        "first_name": subscription.user.first_name,
        "last_name": subscription.user.last_name,
        "course": subscription.course.type.title,
        "course_info": create_course_info(subscription.course),
    }

    if subscription.state == SubscribeState.WAITING_LIST:
        context.update(
            {"waiting_list_position": subscription.get_position_on_waiting_list()}
        )
        if subscription.partner is not None:
            template = "subscription_confirmation_with_partner_waiting_list"
            context.update(
                {
                    "partner_first_name": subscription.partner.first_name,
                    "partner_last_name": subscription.partner.last_name,
                }
            )
        elif subscription.course.type.couple_course:
            template = "subscription_confirmation_without_partner_waiting_list"
        else:
            template = "subscription_confirmation_without_partner_nocouple_waiting_list"

    else:
        if subscription.partner is not None:
            template = "subscription_confirmation_with_partner"
            context.update(
                {
                    "partner_first_name": subscription.partner.first_name,
                    "partner_last_name": subscription.partner.last_name,
                }
            )
        elif subscription.course.type.couple_course:
            template = "subscription_confirmation_without_partner"
        else:
            template = "subscription_confirmation_without_partner_nocouple"

    return send_email(
        to=subscription.user.email,
        reply_to=settings.EMAIL_ADDRESS_COURSE_SUBSCRIPTIONS,
        template=template,
        context=context,
    )


def _build_subscription_context(subscription: Subscribe) -> dict:
    payment_url = (
        (
            "https://"
            + settings.DEPLOYMENT_DOMAIN
            + reverse("payment:subscription_payment", kwargs={"usi": subscription.usi})
        )
        if not subscription.open_amount().is_zero()
        else None
    )
    return {
        "first_name": subscription.user.first_name,
        "last_name": subscription.user.last_name,
        "course": subscription.course.type.title,
        "course_info": create_course_info(subscription.course),
        "payment_url": payment_url,
        "course_type_participant_info_en": subscription.course.type.safe_translation_getter(
            "information_for_participants", language_code="en"
        ),
        "course_type_participant_info_de": subscription.course.type.safe_translation_getter(
            "information_for_participants", language_code="de"
        ),
        "course_participant_info_admin_en": subscription.course.safe_translation_getter(
            "information_for_participants_admin", language_code="en"
        ),
        "course_participant_info_admin_de": subscription.course.safe_translation_getter(
            "information_for_participants_admin", language_code="de"
        ),
        "course_participant_info_teachers_en": subscription.course.safe_translation_getter(
            "information_for_participants_teachers", language_code="en"
        ),
        "course_participant_info_teachers_de": subscription.course.safe_translation_getter(
            "information_for_participants_teachers", language_code="de"
        ),
    }


def send_participation_confirmation(subscription: Subscribe) -> Optional[Email]:
    context = _build_subscription_context(subscription)

    if subscription.partner is not None:
        template = "participation_confirmation_with_partner"
        context.update(
            {
                "partner_first_name": subscription.partner.first_name,
                "partner_last_name": subscription.partner.last_name,
                "partner_info": create_partner_info(subscription),
            }
        )
    elif subscription.course.type.couple_course:
        template = "participation_confirmation_without_partner"
    else:
        template = "participation_confirmation_without_partner_nocouple"

    email_args = {
        "to": subscription.user.email,
        "reply_to": settings.EMAIL_ADDRESS_COURSE_SUBSCRIPTIONS,
        "template": template,
        "context": context,
    }

    if not subscription.open_amount().is_zero():
        with TemporaryFile() as pdf_file:
            to_pdf(create_qrbill_for_subscription(subscription), pdf_file)
            usi = payment_processor.USI_PREFIX + subscription.usi

            return send_email(
                attachments={f"QR-bill-{usi}.pdf": pdf_file}, **email_args
            )

    return send_email(**email_args)


def send_online_payment_successful(subscription: Subscribe) -> Optional[Email]:
    context = {
        "first_name": subscription.user.first_name,
        "last_name": subscription.user.last_name,
        "course": subscription.course.type.title,
    }

    template = "online_payment_successful"

    return send_email(
        to=subscription.user.email,
        reply_to=settings.EMAIL_ADDRESS_FINANCES,
        template=template,
        context=context,
    )


def send_sorry_for_incorrect_reminder(subscription: Subscribe) -> Optional[Email]:
    context = {
        "first_name": subscription.user.first_name,
        "last_name": subscription.user.last_name,
        "course": subscription.course.type.title,
    }

    template = "sorry_incorrect_payment_reminder"

    return send_email(
        to=subscription.user.email,
        reply_to=settings.EMAIL_ADDRESS_FINANCES,
        template=template,
        context=context,
    )


def send_payment_reminder(subscription: Subscribe) -> Optional[Email]:
    context = _build_subscription_context(subscription)
    context["open_amount"] = subscription.open_amount()
    context["reductions"] = subscription.sum_of_reductions()
    context["paid_amount"] = subscription.sum_of_payments()

    template = "payment_reminder"

    with TemporaryFile() as pdf_file:
        to_pdf(create_qrbill_for_subscription(subscription), pdf_file)
        usi = payment_processor.USI_PREFIX + subscription.usi

        return send_email(
            to=subscription.user.email,
            reply_to=settings.EMAIL_ADDRESS_FINANCES,
            template=template,
            context=context,
            attachments={f"QR-bill-{usi}.pdf": pdf_file},
        )


def send_rejection(subscription: Subscribe, reason: str) -> Optional[Email]:
    context = {
        "first_name": subscription.user.first_name,
        "last_name": subscription.user.last_name,
        "course": subscription.course.type.title,
        "course_info": create_course_info(subscription.course),
    }

    template = "rejection_{}".format(reason)

    return send_email(
        to=subscription.user.email,
        reply_to=settings.EMAIL_ADDRESS_COURSE_SUBSCRIPTIONS,
        template=template,
        context=context,
    )


def send_teacher_welcome(teach: Teach) -> Optional[Email]:
    teacher = teach.teacher
    if not teacher.email:
        return None
    course = teach.course

    current_site = "https://" + settings.DEPLOYMENT_DOMAIN
    course_url = current_site + reverse(
        "courses:course_detail", kwargs={"course_id": course.id}
    )
    coursepayment_url = current_site + reverse(
        "payment:coursepayment_detail", kwargs={"course": course.id}
    )
    login_url = current_site + reverse("account_login")
    profile_url = current_site + reverse("edit_profile")

    context = {
        "first_name": teacher.first_name,
        "last_name": teacher.last_name,
        "course": course.type.title,
        "course_internal_name": course.name,
        "course_info": create_course_info(course),
        "course_url": course_url,
        "room_info": course.room.description if course.room else "",
        "room_instructions": course.room.instructions if course.room else "",
        "coursepayment_url": coursepayment_url,
        "login_url": login_url,
        "profile_url": profile_url,
    }

    template = "teacher_welcome"

    return send_email(
        to=teacher.email,
        reply_to=settings.EMAIL_ADDRESS_DANCE_ADMIN,
        template=template,
        context=context,
    )


def detect_rejection_reason(subscription: Subscribe) -> str:
    """
    detect the reason why the subscription is rejected
    :return: the reason as constant from Rejection.Reason
    """
    reason = courses.models.RejectionReason.UNKNOWN
    counts = subscription.course.get_free_places_count()
    if counts and counts == 0:
        reason = courses.models.RejectionReason.OVERBOOKED
    elif subscription.course.type.couple_course and subscription.partner is None:
        reason = courses.models.RejectionReason.NO_PARTNER
    return reason


def create_partner_info(subscription: Subscribe) -> str:
    user = subscription.partner
    lines = []
    if subscription.share_partner_personal_data():
        lines.append(user.get_full_name())
        if user.email:
            lines.append(user.email)
        if user.profile.phone_number:
            lines.append(user.profile.phone_number)
    else:
            lines.append(user.profile.get_first_name_and_initials_last_name())

    return "\n".join(lines)


def create_course_info(course: Course) -> str:
    s = f"{course.type.title}\n{course.format_lessons()}\n"
    if course.room:
        s += f"{course.room}\n"
    s += f"{course.get_period()}\n"
    if course.format_cancellations():
        s += f'{_("Cancellations")}: {course.format_cancellations()}\n'
    if course.format_prices():
        s += f'{_("Costs")}: {course.format_prices()}\n'
    return s.strip("\n")


def send_move_to_waiting_list(subscription: Subscribe) -> Optional[Email]:
    context = {
        "first_name": subscription.user.first_name,
        "course": subscription.course.type.title,
    }

    template = "move_to_waiting_list"

    return send_email(
        to=subscription.user.email,
        reply_to=settings.EMAIL_ADDRESS_COURSE_SUBSCRIPTIONS,
        template=template,
        context=context,
    )
