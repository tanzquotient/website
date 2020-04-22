from django.contrib import admin
from parler.admin import TranslatableAdmin

from email_system.models import TqEmailAddress


@admin.register(TqEmailAddress)
class TqEmailAddressAdmin(TranslatableAdmin):
    model = TqEmailAddress

    list_display = ['email_address', 'description']
    search_fields = ['email_address', 'description']

