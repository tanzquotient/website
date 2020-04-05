from django.utils.translation import ugettext_lazy as _

class Gender:
    MALE = 'm'
    FEMALE = 'w'

    CHOICES = (
        (MALE, _('male')),
        (FEMALE, _('female'))
    )
