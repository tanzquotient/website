# Define a new Group admin
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group, User
from django.forms import ModelForm, ModelMultipleChoiceField

from .admin_actions import update_groups


class GroupForm(ModelForm):
    users = ModelMultipleChoiceField(
        label='Users',
        queryset=User.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            "users", is_stacked=False))

    class Meta:
        model = Group
        exclude = ('permissions', )  # since Django 1.8 this is needed
        widgets = dict()


class GroupFormWithPermissions(ModelForm):
    users = ModelMultipleChoiceField(
        label='Users',
        queryset=User.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            "users", is_stacked=False))

    class Meta:
        model = Group
        exclude = ()  # since Django 1.8 this is needed
        widgets = {
            'permissions': FilteredSelectMultiple(
                "permissions", is_stacked=False),
        }

class TQGroupAdmin(GroupAdmin):
    actions = GroupAdmin.actions + [update_groups]
    form = GroupForm

    def save_model(self, request, obj, form, change):
        # save first to obtain id
        super(GroupAdmin, self).save_model(request, obj, form, change)
        obj.user_set.clear()
        for user in form.cleaned_data['users']:
            obj.user_set.add(user)

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.form.base_fields['users'].initial = [o.pk for o in obj.user_set.all()]
        else:
            self.form.base_fields['users'].initial = []
        if request.user.is_superuser:
            return GroupFormWithPermissions
        return GroupForm

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

# Re-register GroupAdmin
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass
admin.site.register(Group, TQGroupAdmin)