from django.contrib import admin
from parler.admin import TranslatableAdmin

from partners.models.partner import Partner


@admin.register(Partner)
class PartnerAdmin(TranslatableAdmin):
    model = Partner

    list_display = ["name", "url"]
    search_fields = ["name"]
