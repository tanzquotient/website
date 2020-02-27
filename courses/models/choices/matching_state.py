class MatchingState:
    UNKNOWN = 'unknown'
    COUPLE = 'couple'
    TO_MATCH = 'to_match'
    TO_REMATCH = 'to_rematch'
    MATCHED = 'matched'
    NOT_REQUIRED = 'not_required'

    CHOICES = (
        (UNKNOWN, 'Unknown'),
        (COUPLE, 'Couple'),
        (TO_MATCH, 'To match'),
        (TO_REMATCH, 'To rematch'),
        (MATCHED, 'Matched'),
        (NOT_REQUIRED, 'Not required')
    )

    MATCHED_STATES = [COUPLE, MATCHED]
    TO_MATCH_STATES = [TO_MATCH, TO_REMATCH]
