from groups.services import update_groups as service_update_groups
from groups.services import duplicate_groups as service_duplicate_groups


def update_groups(admin, request, queryset):
    service_update_groups(queryset=queryset)

def duplicate_groups(admin, request, queryset):
    service_duplicate_groups(queryset=queryset)


update_groups.short_description = "Update groups"
duplicate_groups.short_description = "Duplicate groups"