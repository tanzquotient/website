from groups.services import update_groups as service_update_groups

def update_groups(admin, request, queryset):
    service_update_groups(queryset=queryset)

update_groups.short_description = 'Update groups'