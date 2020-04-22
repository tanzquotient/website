import logging

from django.contrib.auth.models import Group

from courses.models import UserProfile
from ..definitions import GroupDefinitions

log = logging.getLogger('update_groups')


def update_groups(queryset=None):

    log.info("Updating groups")

    # All groups
    if queryset is None:
        for group_definition in GroupDefinitions.DEFINITIONS:
            Group.objects.get_or_create(name=group_definition.name)
        queryset = Group.objects

    for group_definition in GroupDefinitions.DEFINITIONS:
        if group_definition.is_manual():
            continue

        group = queryset.filter(name=group_definition.name)
        if not group.exists():
            continue

        log.info("Updating group " + group_definition.name)

        group = group.get()
        group.user_set.clear()
        for profile in UserProfile.objects.all():
            user = profile.user
            if group_definition.matches(user):
                group.user_set.add(user)

        log.info("Updating group finished. Number of users in group " + str(group.user_set.count()))
