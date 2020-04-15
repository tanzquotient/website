from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class EmailSystemConfig(AppConfig):
    name = 'email_system'
    verbose_name = _('Emails')
