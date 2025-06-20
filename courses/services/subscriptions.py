from typing import Iterable

from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext as _
from django.utils import timezone
from reversion import revisions as reversion

from courses import models as models
from courses.emailcenter import (
    send_subscription_confirmation,
    send_participation_confirmation,
    detect_rejection_reason,
    send_rejection,
)
from courses.models import (
    Subscribe,
    LeadFollow,
    SingleCouple,
    MatchingState,
    SubscribeState,
    Course,
)
from courses.services.general import log


@transaction.atomic
def subscribe(course: Course, user: User, data: dict) -> Subscribe:
    """Enrolls a user (and optionally a partner) in a course"""

    try:
        user_subscription = Subscribe.objects.get(user=user, course=course)
    except Subscribe.DoesNotExist:
        user_subscription = Subscribe(user=user, course=course)

    # let the save method set the state of the subscription and reset the date
    user_subscription.state = None
    user_subscription.date = timezone.localtime(timezone.now())

    user_subscription.lead_follow = data.get("lead_follow", LeadFollow.NO_PREFERENCE)
    user_subscription.experience = data.get("experience", None)
    user_subscription.comment = data.get("comment", None)

    # Handle couple subscription
    if data["single_or_couple"] == SingleCouple.COUPLE:
        partner = User.objects.get(email__iexact=data["partner_email"])

        try:
            partner_subscription = Subscribe.objects.get(user=partner, course=course)
        except Subscribe.DoesNotExist:
            partner_subscription = Subscribe(user=partner, course=course)

        # let the save method set the state of the subscription and reset the date
        partner_subscription.state = None
        partner_subscription.date = timezone.localtime(timezone.now())

        partner_subscription.lead_follow = LeadFollow.partner(
            user_subscription.lead_follow
        )
        partner_subscription.experience = user_subscription.partner
        partner_subscription.comment = user_subscription.comment

        # Link subscriptions
        user_subscription.partner = partner
        partner_subscription.partner = user
        user_subscription.matching_state = MatchingState.COUPLE
        partner_subscription.matching_state = MatchingState.COUPLE

        # if the course has a place for a couple,
        # set state as NEW, else put both subscribes
        # on the waiting list
        subscribe_state = (
            SubscribeState.NEW
            if course.has_free_places_for_followers
            and course.has_free_places_for_leaders
            else SubscribeState.WAITING_LIST
        )
        partner_subscription.state = subscribe_state
        user_subscription.state = subscribe_state

        # Finish partner subscription
        partner_subscription.save()

    # Finish user subscriptiong
    user_subscription.derive_matching_state()
    user_subscription.save()
    send_subscription_confirmation(user_subscription)
    if data["single_or_couple"] == SingleCouple.COUPLE:
        send_subscription_confirmation(partner_subscription)

    return user_subscription


def confirm_subscription(
    subscription: Subscribe,
    request: HttpRequest = None,
    allow_single_in_couple_course: bool = False,
) -> bool:
    """sends a confirmation mail if subscription is confirmed (by some other method)
    and no confirmation mail was sent before"""
    # check: only people with partner are confirmed (in couple courses)
    if (
        not allow_single_in_couple_course
        and subscription.course.type.couple_course
        and subscription.partner is None
    ):
        raise NoPartnerException()

    if subscription.state == models.SubscribeState.NEW:
        with reversion.create_revision():
            subscription.generate_price_to_pay()  # Make sure the price is generated
            new_state = (
                SubscribeState.COMPLETED
                if not subscription.price_to_pay
                else SubscribeState.CONFIRMED
            )
            subscription.state = new_state
            subscription.save()

            reversion.set_comment(f"Updated state to {new_state}")

        mail = send_participation_confirmation(subscription)
        if mail:
            # log that we sent the confirmation
            c = models.Confirmation(subscription=subscription, mail=mail)
            c.save()
            return True
        else:
            return False
    else:
        return False


def confirm_subscriptions(
    subscriptions: QuerySet[Subscribe],
    request: HttpRequest = None,
    allow_single_in_couple_course: bool = False,
) -> None:
    no_partner_count = 0
    confirmed_count = 0
    for subscription in subscriptions:
        try:
            if confirm_subscription(
                subscription, request, allow_single_in_couple_course
            ):
                confirmed_count += 1
        except NoPartnerException:
            no_partner_count += 1

    if no_partner_count:  # if any subscriptions not confirmed due to missing partner
        log.warning(MESSAGE_NO_PARTNER_SET.format(no_partner_count))
        if request:
            messages.add_message(
                request,
                messages.WARNING,
                MESSAGE_NO_PARTNER_SET.format(no_partner_count),
            )
    if confirmed_count:
        messages.add_message(
            request,
            messages.SUCCESS,
            _("{} of {} confirmed successfully").format(
                confirmed_count, len(subscriptions)
            ),
        )


def unconfirm_subscriptions(
    subscriptions: QuerySet[Subscribe], request: HttpRequest = None
) -> None:
    for s in subscriptions.all():
        if s.state == models.SubscribeState.CONFIRMED:
            with reversion.create_revision():
                s.state = models.SubscribeState.NEW
                s.save()

                reversion.set_comment("Subscription unconfirmed")


def reject_subscription(
    subscription: Subscribe, reason: str = None, send_email: bool = True
) -> None:
    """sends a rejection mail if subscription is rejected (by some other method)
    and no rejection mail was sent before"""
    if subscription.partner is not None:
        partner_subscription = subscription.get_partner_subscription()
        with reversion.create_revision():
            partner_subscription.partner = None
            partner_subscription.matching_state = MatchingState.TO_REMATCH
            partner_subscription.save()

            reversion.set_comment(
                "Subscription to rematch following rejection of partner"
                f"with reason {reason}"
            )

    with reversion.create_revision():
        subscription.state = (
            models.SubscribeState.TO_REIMBURSE
            if subscription.state == models.SubscribeState.PAID
            else models.SubscribeState.REJECTED
        )
        if subscription.partner is not None:
            subscription.partner = None
            subscription.matching_state = MatchingState.TO_REMATCH

        subscription.save()

        reversion.set_comment(f"Subscription rejected with reason {reason}")

    if not reason:
        reason = detect_rejection_reason(subscription)
    c = models.Rejection(subscription=subscription, reason=reason, mail_sent=False)
    c.save()

    subscription.course.update_waiting_list()

    if (
        send_email
        and models.Rejection.objects.filter(
            subscription=subscription, mail_sent=True
        ).count()
        == 0
    ):
        # if ensures that no mail was ever sent due to a rejection to this user

        # save if we sent the mail
        c.mail = send_rejection(subscription, reason)
        c.mail_sent = c.mail is not None
        c.save()


def reject_subscriptions(
    subscriptions: Iterable[Subscribe], reason: str = None, send_email: bool = True
) -> None:
    """same as reject_subscription, but for multiple subscriptions at once"""
    for subscription in subscriptions:
        reject_subscription(subscription, reason, send_email)


def unreject_subscriptions(
    subscriptions: Iterable[Subscribe], request: HttpRequest = None
) -> None:
    unrejected_count = 0
    for subscription in subscriptions:
        if subscription.state == models.SubscribeState.REJECTED:
            with reversion.create_revision():
                subscription.state = None
                subscription.save()
                reversion.set_comment("Subscription unrejected")

            unrejected_count += 1
    if unrejected_count:
        messages.add_message(
            request,
            messages.SUCCESS,
            _("{} unrejected successfully").format(unrejected_count),
        )


class NoPartnerException(Exception):
    def __str__(self) -> str:
        return "This subscription has no partner set"


MESSAGE_NO_PARTNER_SET = _("{} subscriptions were not confirmed because no partner set")
