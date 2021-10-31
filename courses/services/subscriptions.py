from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from django.utils.translation import gettext as _

from courses import models as models
from courses.emailcenter import send_subscription_confirmation, send_participation_confirmation, \
    detect_rejection_reason, send_rejection
from courses.models import Subscribe, LeadFollow, SingleCouple, MatchingState
from courses.services.general import log


@transaction.atomic
def subscribe(course, user, data):
    """Enrolls a user (and optionally a partner) in a course"""

    user_subscription = Subscribe(
        user=user,
        course=course,
        lead_follow=data.get('lead_follow', LeadFollow.NO_PREFERENCE),
        experience=data.get('experience', None),
        comment=data.get('experience', None),
    )

    # Handle couple subscription
    if data['single_or_couple'] == SingleCouple.COUPLE:
        partner = User.objects.get(email=data['partner_email'])

        partner_subscription = Subscribe(
            user=partner,
            course=course,
            lead_follow=LeadFollow.partner(data.get('lead_follow', LeadFollow.NO_PREFERENCE)),
            experience=data.get('experience', None),
            comment=data.get('experience', None),
        )

        # Link subscriptions
        user_subscription.partner = partner
        partner_subscription.partner = user
        user_subscription.matching_state = MatchingState.COUPLE
        partner_subscription.matching_state = MatchingState.COUPLE

        # Finish partner subscription
        partner_subscription.save()
        send_subscription_confirmation(partner_subscription)

    # Finish user subscription
    user_subscription.derive_matching_state()
    user_subscription.save()
    send_subscription_confirmation(user_subscription)

    return user_subscription


def confirm_subscription(subscription, request=None, allow_single_in_couple_course=False):
    '''sends a confirmation mail if subscription is confirmed (by some other method) and no confirmation mail was sent before'''
    # check: only people with partner are confirmed (in couple courses)
    if not allow_single_in_couple_course and subscription.course.type.couple_course and subscription.partner is None:
        raise NoPartnerException()

    if subscription.state == models.SubscribeState.NEW:
        subscription.state = models.SubscribeState.CONFIRMED
        subscription.save()

        m = send_participation_confirmation(subscription)
        if m:
            # log that we sent the confirmation
            c = models.Confirmation(subscription=subscription, mail=m)
            c.save()
            return True
        else:
            return False
    else:
        return False


def confirm_subscriptions(subscriptions, request=None, allow_single_in_couple_course=False):
    no_partner_count = 0
    confirmed_count = 0
    for subscription in subscriptions:
        try:
            if confirm_subscription(subscription, request, allow_single_in_couple_course):
                confirmed_count += 1
        except NoPartnerException as e:
            no_partner_count += 1

    if no_partner_count:  # if any subscriptions not confirmed due to missing partner
        log.warning(MESSAGE_NO_PARTNER_SET.format(no_partner_count))
        if request:
            messages.add_message(request, messages.WARNING, MESSAGE_NO_PARTNER_SET.format(no_partner_count))
    if confirmed_count:
        messages.add_message(request, messages.SUCCESS,
                             _(u'{} of {} confirmed successfully').format(confirmed_count, len(subscriptions)))


def unconfirm_subscriptions(subscriptions, request=None):
    for s in subscriptions.all():
        if s.state == models.SubscribeState.CONFIRMED:
            s.state = models.SubscribeState.NEW
            s.save()


def reject_subscription(subscription, reason=None, send_email=True):
    '''sends a rejection mail if subscription is rejected (by some other method) and no rejection mail was sent before'''
    subscription.state = models.SubscribeState.REJECTED
    subscription.save()
    if not reason:
        reason = detect_rejection_reason(subscription)
    c = models.Rejection(subscription=subscription, reason=reason, mail_sent=False)
    c.save()

    if send_email and models.Rejection.objects.filter(subscription=subscription, mail_sent=True).count() == 0:
        # if ensures that no mail was ever sent due to a rejection to this user

        # save if we sent the mail
        c.mail = send_rejection(subscription, reason)
        c.mail_sent = c.mail is not None
        c.save()


def reject_subscriptions(subscriptions, reason=None, send_email=True):
    '''same as reject_subscription, but for multiple subscriptions at once'''
    for subscription in subscriptions:
        reject_subscription(subscription, reason, send_email)


def unreject_subscriptions(subscriptions, request=None):
    unrejected_count = 0
    for subscription in subscriptions:
        if subscription.state == models.SubscribeState.REJECTED:
            subscription.state = models.SubscribeState.NEW
            subscription.save()
            unrejected_count += 1
    if unrejected_count:
        messages.add_message(request, messages.SUCCESS,
                             _(u'{} unrejected successfully').format(unrejected_count))


class NoPartnerException(Exception):
    def __str__(self):
        return 'This subscription has no partner set'


MESSAGE_NO_PARTNER_SET = _(u'{} subscriptions were not confirmed because no partner set')