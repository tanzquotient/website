import logging

from django.contrib.auth.models import Group
from copy import deepcopy

log = logging.getLogger("tq")

def duplicate_groups(queryset=None) -> None:
    for group in queryset:
        suffix = 0
        while True:
            new_group_name = group.name + "_copy" + ("" if suffix == 0 else "_" + str(suffix))
            if Group.objects.filter(name=new_group_name).count() == 0:
                break
            else:
                suffix += 1

        new_group = Group.objects.create(
            name = new_group_name
        )
        new_group.permissions.add(*group.permissions.all())
        new_group.user_set.add(*group.user_set.all())
