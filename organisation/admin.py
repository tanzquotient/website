from django.contrib import admin

from organisation.models import Function


@admin.register(Function)
class FunctionAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'active', 'user',)
