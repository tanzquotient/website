import logging

from django.contrib.auth.models import Group

from courses.models import UserProfile

from ..definitions import GroupDefinitions

log = logging.getLogger("update_groups")


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

        matching_user_ids = {
            profile.user_id
            for profile in UserProfile.objects.select_related("user").iterator(
                chunk_size=500
            )
            if group_definition.matches(profile.user)
        }
        current_user_ids = set(group.user_set.values_list("id", flat=True))

        to_add = matching_user_ids - current_user_ids
        to_remove = current_user_ids - matching_user_ids
        if to_add:
            group.user_set.add(*to_add)
        if to_remove:
            group.user_set.remove(*to_remove)

        log.info(
            "Updating group finished. Number of users in group "
            + str(group.user_set.count())
        )
