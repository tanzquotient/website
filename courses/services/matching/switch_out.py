from django.db import transaction
from reversion import revisions as reversion

from courses.models import MatchingState, Subscribe, SubscribeState
from courses.services.matching.change_matching import _unmatch_person
from courses.services.subscriptions import confirm_subscription, reject_subscription


@transaction.atomic
def switch_out_partner(
    confirmed_sub: Subscribe,
    new_sub: Subscribe,
    partner_sub: Subscribe,
    reason: str,
    send_email: bool = True,
) -> None:
    """Replace confirmed_sub with new_sub as the partner of partner_sub.

    Steps:
    1. Admit new_sub from waiting list if needed (WAITING_LIST → NEW)
    2. Unmatch confirmed_sub and partner_sub
    3. Match new_sub with partner_sub
    4. Confirm new_sub only if confirmed_sub was CONFIRMED/PAID (mirrors outgoing state)
    5. Reject confirmed_sub with the given reason
    """
    # Capture before any mutations — _unmatch_person doesn't change state,
    # but reading it here makes the intent explicit.
    should_confirm = confirmed_sub.state in (
        SubscribeState.CONFIRMED,
        SubscribeState.PAID,
    )

    if new_sub.state == SubscribeState.WAITING_LIST:
        with reversion.create_revision():
            new_sub.state = SubscribeState.NEW
            new_sub.save()
            reversion.set_comment("Admitted from waiting list for partner switch-out")

    _unmatch_person(confirmed_sub)
    _unmatch_person(partner_sub)

    with reversion.create_revision():
        new_sub.partner = partner_sub.user
        new_sub.matching_state = MatchingState.MATCHED
        new_sub.save()
        reversion.set_comment("Matched as part of partner switch-out")

    with reversion.create_revision():
        partner_sub.partner = new_sub.user
        partner_sub.matching_state = MatchingState.MATCHED
        partner_sub.save()
        reversion.set_comment("Re-matched as part of partner switch-out")

    if should_confirm:
        confirm_subscription(new_sub)

    reject_subscription(confirmed_sub, reason, send_email)
