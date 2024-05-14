class GroupEmailState:
    DRAFT = "draft"
    QUEUED = "queued"
    SENDING = "sending"
    SENT = "sent"

    CHOICES = (
        (DRAFT, "Draft"),
        (QUEUED, "Queued"),
        (SENDING, "Sending"),
        (SENT, "Sent"),
    )
