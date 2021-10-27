from django.utils.translation import gettext_lazy as _


class Gender:
    MALE = 'm'
    FEMALE = 'w'
    DIVERSE = 'd'

    CHOICES = (
        (MALE, _('male')),
        (FEMALE, _('female')),
        (DIVERSE, _('diverse'))
    )
