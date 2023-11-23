from django.utils.translation import gettext_lazy as _


class OfferingType:
    REGULAR = "reg"
    IRREGULAR = "irr"
    PARTNER = "p"

    CHOICES = (
        (REGULAR, _("Regular (weekly)")),
        (IRREGULAR, _("Irregular (e.g. workshops)")),
        (PARTNER, _("Partner (external)")),
    )
