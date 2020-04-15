# Define a new User admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from courses.admin import UserProfileInline, SubscribeInlineForUser
from courses.admin_actions import make_inactive


class TQUserAdmin(UserAdmin):
    list_display = ('id',) + UserAdmin.list_display + ('is_active',)
    inlines = list(UserAdmin.inlines) + [UserProfileInline, SubscribeInlineForUser]
    list_filter = UserAdmin.list_filter + ('profile__newsletter', 'profile__get_involved')
    actions = [make_inactive] + UserAdmin.actions

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        disabled_fields = set()

        # Prevent non-superusers from editing other permissions
        if not is_superuser:
            disabled_fields |= {
                'username',
                'is_superuser',
                'user_permissions',
            }

        # Prevent non-superusers from editing their own permissions
        if not is_superuser and obj is not None and obj == request.user:
            disabled_fields |= {
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            }

        for f in disabled_fields:
            if f in form.base_fields:
                form.base_fields[f].disabled = True

        return form


# Re-register UserAdmin
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass
admin.site.register(User, TQUserAdmin)