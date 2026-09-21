from django.contrib.admin import AdminSite
from django.contrib.admin.apps import AdminConfig
from django.contrib.admin.views.autocomplete import AutocompleteJsonView
from django.contrib.auth import get_user_model


class FullNameAutocompleteJsonView(AutocompleteJsonView):
    def serialize_result(self, obj, to_field_name):
        User = get_user_model()

        if isinstance(obj, User):
            return {
                "id": str(getattr(obj, to_field_name)),
                "text": obj.get_full_name() or obj.get_username(),
            }

        return super().serialize_result(obj, to_field_name)


class TQAdminSite(AdminSite):
    def autocomplete_view(self, request):
        return FullNameAutocompleteJsonView.as_view(admin_site=self)(request)


class TQAdminConfig(AdminConfig):
    default_site = "tq_website.admin_config.TQAdminSite"
