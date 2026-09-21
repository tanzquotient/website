# Define a new User admin
from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from hijack.contrib.admin import HijackUserAdminMixin

from courses.admin_actions import make_inactive
from courses.models import Subscribe, UserProfile


class UserFullNameChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_full_name() or obj.get_username()


class UserFullNameMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.get_full_name() or obj.get_username()


class UserFullNameAdminMixin:
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        User = get_user_model()

        if db_field.remote_field and db_field.remote_field.model == User:
            kwargs["form_class"] = UserFullNameChoiceField

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        User = get_user_model()

        if db_field.remote_field and db_field.remote_field.model == User:
            kwargs["form_class"] = UserFullNameMultipleChoiceField

        return super().formfield_for_manytomany(db_field, request, **kwargs)


class SubscribeInlineForUser(admin.TabularInline):
    model = Subscribe
    extra = 1
    fk_name = "user"

    raw_id_fields = ("course", "partner")
    readonly_fields = (
        "state",
        "matching_state",
        "usi",
    )


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    readonly_fields = ["address", "bank_account"]


class TQUserAdmin(HijackUserAdminMixin, UserAdmin):
    list_display = ("id",) + UserAdmin.list_display + ("is_active",)
    inlines = list(UserAdmin.inlines) + [UserProfileInline, SubscribeInlineForUser]
    list_filter = UserAdmin.list_filter + (
        "profile__newsletter",
        "profile__get_involved",
    )
    actions = [make_inactive] + list(UserAdmin.actions)

    def get_hijack_user(self, instance) -> User:
        return instance

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        disabled_fields = set()

        # Prevent non-superusers from editing other permissions
        if not is_superuser:
            disabled_fields |= {
                "username",
                "is_superuser",
                "user_permissions",
            }

        # Prevent non-superusers from editing their own permissions
        if not is_superuser and obj is not None and obj == request.user:
            disabled_fields |= {
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
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
