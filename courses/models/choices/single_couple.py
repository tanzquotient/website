from django.utils.translation import gettext_lazy as _


class SingleCouple:
    SINGLE = 's'
    COUPLE = 'c'

    CHOICES = (
        (SINGLE, _('single')),
        (COUPLE, _('couple')),
    )
