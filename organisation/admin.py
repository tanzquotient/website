from django.contrib import admin
from parler.admin import TranslatableAdmin

from organisation.models import Function


class UserInline(admin.TabularInline):
    model = Function.users.through
    raw_id_fields = ("user",)
    extra = 0


@admin.register(Function)
class FunctionAdmin(TranslatableAdmin):
    list_display = (
        "name",
        "email",
        "names",
    )
    inlines = (UserInline,)
    exclude = ("users",)
