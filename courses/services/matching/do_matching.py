import logging

from django.contrib import messages
from django.db import transaction
from django.utils.translation import gettext as _

from courses import models as models
from courses.models import LeadFollow

log = logging.getLogger('matching')


def _get_lists_for_partition(subscribes):
    """
    Returns lists needed for partitioning.
        'a' is the larger set out of leaders and followers
        'b' is the other set from leaders/followers
    """
    leaders = [s for s in subscribes if s.lead_follow == LeadFollow.LEAD]
    followers = [s for s in subscribes if s.lead_follow == LeadFollow.FOLLOW]
    no_preference = [s for s in subscribes if s.lead_follow == LeadFollow.NO_PREFERENCE]

    a = leaders
    b = followers

    # We want to ensure |a| >= |b|
    if len(a) < len(b):
        a, b = b, a

    return a, b, no_preference


def _partition_subscribes(subscribes):
    """
    Returns two lists a, b such that len(a) = len(b).
    Moreover, every entry in a can be matched with any entry in b according to the
    respective lead/follow preference.

    If there are to many leaders or followers, the newest subscriptions are discarded
    If there is an odd number of subscriptions, the newest subscription is discarded
    """
    log.info("got {} subscribes".format(len(subscribes)))

    a, b, no_preference = _get_lists_for_partition(subscribes)
    log.info("sizes: |a| = {}, |b| = {}, |no_preference| = {}".format(len(a), len(b), len(no_preference)))

    if len(a) >= len(b) + len(no_preference):
        num_pairs = len(b) + len(no_preference)
        a = a[0:num_pairs]
        b += no_preference
        log.info("added all with no preference to smaller set. Limiting larger set to {} subscribes".format(num_pairs))

    else:  # diff := len(a) - len(b) < len(no_preference)

        # If odd number: remove last subscribe
        if len(subscribes) % 2 == 1:
            log.info("odd number of subscriptions, dropping '{}'".format(subscribes[-1]))
            subscribes = subscribes[0:-1]
            a, b, no_preference = _get_lists_for_partition(subscribes)
            log.info("new sizes: |a| = {}, |b| = {}, |no_preference| = {}".format(len(a), len(b), len(no_preference)))

        diff = len(a) - len(b)
        assign_to_a_count = (len(no_preference) - diff) // 2
        log.info("assigning {} subscribe(s) with no preference to a. The remaining {} will be assigned to b"
                 .format(assign_to_a_count, len(no_preference) - assign_to_a_count))

        a += no_preference[0:assign_to_a_count]
        b += no_preference[assign_to_a_count:]

    log.info("found partition with |a| = {}, |b| = {}.".format(len(a), len(b)))
    return a, b


@transaction.atomic
def _match_for_course(subscriptions, course_id):
    """
    Partitions the single subscribes into two lists.
    Afterwards, the lists are merged based on height
    """
    to_match = list(subscriptions.filter(course__id=course_id).single().order_by('date'))

    a, b = _partition_subscribes(to_match)
    assert len(a) == len(b)

    def sort_key(subscribe):
        default_value = 250  # people of unknown height should be the last in the list
        return subscribe.user.profile.body_height or default_value

    a.sort(key=sort_key)
    b.sort(key=sort_key)

    for (subscribe_a, subscribe_b) in zip(a, b):

        assert LeadFollow.is_compatible(subscribe_a.lead_follow, subscribe_b.lead_follow)
        log.info("going to match '{}' with '{}'".format(subscribe_a, subscribe_b))

        subscribe_a.partner = subscribe_b.user
        subscribe_a.matching_state = models.MatchingState.MATCHED
        subscribe_a.save()

        subscribe_b.partner = subscribe_a.user
        subscribe_b.matching_state = models.MatchingState.MATCHED
        subscribe_b.save()

    match_count = len(a)
    log.info("match count = {}".format(match_count))
    return match_count


def match_partners(subscriptions, request=None):
    courses = subscriptions.values_list('course', flat=True)
    match_count = 0
    for course_id in set(courses):
        log.info("matching for course id {}".format(course_id))
        match_count += _match_for_course(subscriptions, course_id)

    log.info('{} couples matched successfully'.format(match_count))
    messages.add_message(request, messages.SUCCESS, _('{} couples matched successfully').format(match_count))
