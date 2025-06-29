from django.utils.translation import gettext_lazy as _


class AttendanceState:
    PRESENT = "present"
    ABSENT_EXCUSED = "absent_excused"
    ABSENT_NOT_EXCUSED = "absent_not_excused"
    REPLACEMENT = "replacement"

    CHOICES = (
        (PRESENT, _("present")),
        (ABSENT_EXCUSED, _("absent, excused")),
        (ABSENT_NOT_EXCUSED, _("absent, not excused")),
        (REPLACEMENT, _("replacement")),
    )

    NAMES = {key: name for key, name in CHOICES}

    PRESENT_STATES = [PRESENT, REPLACEMENT]
    ABSENT_STATES = [ABSENT_EXCUSED, ABSENT_NOT_EXCUSED]
