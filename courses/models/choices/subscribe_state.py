class SubscribeState:
    NEW = 'new'
    CONFIRMED = 'confirmed'
    PAYED = 'payed'
    COMPLETED = 'completed'
    REJECTED = 'rejected'
    TO_REIMBURSE = 'to_reimburse'

    CHOICES = (
        (NEW, 'new'),
        (CONFIRMED, 'confirmed (to pay)'),
        (PAYED, 'payed'),
        (COMPLETED, 'completed'),
        (REJECTED, 'rejected'),
        (TO_REIMBURSE, 'to reimburse'))

    ACCEPTED_STATES = [CONFIRMED, PAYED, COMPLETED]
    REJECTED_STATES = [REJECTED, TO_REIMBURSE]
    PAID_STATES = [PAYED, TO_REIMBURSE, COMPLETED]
