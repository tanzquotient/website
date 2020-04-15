from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class GroupsConfig(AppConfig):
    name = 'groups'
    verbose_name = _('Groups')
