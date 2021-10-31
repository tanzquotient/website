from django.contrib import messages
from django.utils.translation import gettext as _

from courses import models as models


def correct_matching_state_to_couple(subscriptions, request=None):
    corrected_count = 0

    for s in subscriptions.all():
        partner_subs = subscriptions.filter(user=s.partner, course=s.course)
        if partner_subs.count() == 1:
            partner_sub = partner_subs.first()
            # because we update matching state iteratively, we have to allow also COUPLE State
            allowed_states = [models.MatchingState.MATCHED, models.MatchingState.COUPLE]
            if s.matching_state == models.MatchingState.MATCHED and partner_sub.matching_state in allowed_states:
                s.matching_state = models.MatchingState.COUPLE
                s.save()
                corrected_count += 1

    if corrected_count:
        messages.add_message(request, messages.SUCCESS,
                             _(u'{} subscriptions ({} couples) corrected successfully').format(corrected_count,
                                                                                               corrected_count / 2))


def unmatch_partners(subscriptions, request):
    corrected_count = 0
    invalid_state_count = 0
    invalid_matching_state_count = 0
    for s in subscriptions.all():
        if s.state == models.SubscribeState.NEW:
            allowed_states = [models.MatchingState.MATCHED]
            partner_subs = subscriptions.filter(user=s.partner, course=s.course)
            if partner_subs.count() == 1 and s.matching_state in allowed_states and partner_subs.first().matching_state in allowed_states:
                _unmatch_person(s)
                _unmatch_person(partner_subs.first())
                corrected_count += 1
            else:
                invalid_matching_state_count += 1
        else:
            invalid_state_count += 1

    invalid_matching_state_count -= corrected_count  # subtract wrongly counted errors

    if corrected_count:
        messages.add_message(request, messages.SUCCESS,
                             _(u'{} couples unmatched successfully').format(corrected_count))
    if invalid_state_count:
        messages.add_message(request, messages.WARNING,
                             _(u'{} subscriptions can not be unmatched because already CONFIRMED').format(
                                 invalid_state_count))
    if invalid_matching_state_count:
        messages.add_message(request, messages.WARNING,
                             _(u'{} subscriptions can not be unmatched because invalid matching state').format(
                                 invalid_matching_state_count))


def breakup_couple(subscriptions, request):
    corrected_count = 0
    invalid_state_count = 0
    invalid_matching_state_count = 0
    for s in subscriptions.all():
        if s.state == models.SubscribeState.NEW:
            allowed_states = [models.MatchingState.COUPLE]
            partner_subs = subscriptions.filter(user=s.partner, course=s.course)
            if partner_subs.count() == 1 and s.matching_state in allowed_states and partner_subs.first().matching_state in allowed_states:
                _unmatch_person(s)
                _unmatch_person(partner_subs.first())
                corrected_count += 1
            else:
                invalid_matching_state_count += 1
        else:
            invalid_state_count += 1

    invalid_matching_state_count -= corrected_count  # subtract wrongly counted errors

    if corrected_count:
        messages.add_message(request, messages.SUCCESS,
                             _(u'{} couples broken up successfully').format(corrected_count))
    if invalid_state_count:
        messages.add_message(request, messages.WARNING,
                             _(u'{} couples can not be broken up because already CONFIRMED').format(
                                 invalid_state_count))
    if invalid_matching_state_count:
        messages.add_message(request, messages.WARNING,
                             _(u'{} couples can not be broken up because invalid matching state').format(
                                 invalid_matching_state_count))


def _unmatch_person(subscription):
    subscription.partner = None
    subscription.matching_state = models.MatchingState.TO_REMATCH
    subscription.save()