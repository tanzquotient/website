class SubscribeState:
    NEW = "new"
    WAITING_LIST = "waiting_list"
    CONFIRMED = "confirmed"
    PAID = "payed"
    COMPLETED = "completed"
    REJECTED = "rejected"
    TO_REIMBURSE = "to_reimburse"

    CHOICES = (
        (NEW, "new"),
        (WAITING_LIST, "waiting list"),
        (CONFIRMED, "confirmed (to pay)"),
        (PAID, "paid"),
        (COMPLETED, "completed"),
        (REJECTED, "rejected"),
        (TO_REIMBURSE, "to reimburse"),
    )

    ACCEPTED_STATES = [CONFIRMED, PAID, COMPLETED]
    REJECTED_STATES = [REJECTED, TO_REIMBURSE]
    PAID_STATES = [PAID, TO_REIMBURSE, COMPLETED]
    TO_PAY_STATES = [CONFIRMED]
