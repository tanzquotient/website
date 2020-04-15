# Define a new Group admin
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group

from .admin_actions import update_groups


class TQGroupAdmin(GroupAdmin):
    actions = GroupAdmin.actions + [update_groups]

# Re-register GroupAdmin
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass
admin.site.register(Group, TQGroupAdmin)