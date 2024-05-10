class GroupEmailState:
    DRAFT = "draft"
    QUEUED = "queued"
    SENT = "sent"

    CHOICES = (
        (DRAFT, "Draft"),
        (QUEUED, "Queued"),
        (SENT, "Sent"),
    )
