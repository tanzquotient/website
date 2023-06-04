class RejectionReason:
    UNKNOWN = "unknown"
    OVERBOOKED = "overbooked"
    NO_PARTNER = "no_partner"
    USER_CANCELLED = "user_cancelled"
    ILLEGITIMATE = "illegitimate"
    BANNED = "banned"
    COURSE_CANCELLED = "course_cancelled"

    CHOICES = (
        (UNKNOWN, "Unknown"),
        (OVERBOOKED, "Overbooked"),
        (NO_PARTNER, "No partner found"),
        (USER_CANCELLED, "User cancelled the subscription"),
        (ILLEGITIMATE, "Users subscription is illegitimate"),
        (BANNED, "User is banned"),
        (COURSE_CANCELLED, "Course was cancelled"),
    )
