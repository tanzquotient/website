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
