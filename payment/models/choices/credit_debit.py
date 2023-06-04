class CreditDebit:
    UNKNOWN = "unknown"
    CREDIT = "credit"
    DEBIT = "debit"

    CHOICES = (
        (UNKNOWN, UNKNOWN),
        (CREDIT, "credit (incoming money)"),
        (DEBIT, "debit (outgoing money)"),
    )
