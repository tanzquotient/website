from django.contrib import admin

from organisation.models import Function

class UserInline(admin.TabularInline):
    model = Function.users.through
    raw_id_fields = ('user',)
    extra = 0

@admin.register(Function)
class FunctionAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'active', 'format_users',)
    inlines = (UserInline,)
    exclude = ('users',)
