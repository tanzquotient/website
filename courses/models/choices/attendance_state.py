from django.utils.translation import gettext_lazy as _


class AttendanceState:
    PRESENT = "present"
    ABSENT_EXCUSED = "absent_excused"
    ABSENT_NOT_EXCUSED = "absent_not_excused"
    REPLACEMENT_CONFIRMED = "replacement_confirmed"
    REPLACEMENT_PENDING = "replacement_pending"

    CHOICES = (
        (PRESENT, _("present")),
        (ABSENT_EXCUSED, _("absent, excused")),
        (ABSENT_NOT_EXCUSED, _("absent, not excused")),
        (REPLACEMENT_CONFIRMED, _("replacement confirmed")),
        (REPLACEMENT_PENDING, _("replacement pending")),
    )

    NAMES = {key: name for key, name in CHOICES}

    PRESENT_STATES = [PRESENT, REPLACEMENT_CONFIRMED]
    ABSENT_STATES = [ABSENT_EXCUSED, ABSENT_NOT_EXCUSED]
    PENDING_STATES = [REPLACEMENT_PENDING]
