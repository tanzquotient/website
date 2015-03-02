from django.contrib import admin

from courses.models import *

import services

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

def confirm_subscriptions(modeladmin, request, queryset):
    # this is directly executed with database query, does not trigger signals!
    queryset.update(confirmed=True)
    
    # manually send confirmation mails
    services.confirm_subscriptions(queryset)
        
confirm_subscriptions.short_description = "Confirm selected subscriptions"

def set_subscriptions_as_payed(modeladmin, request, queryset):
    queryset.update(payed=True)
set_subscriptions_as_payed.short_description = "Set selected subscriptions as payed"

def export_confirmed_subscriptions_csv(modeladmin, request, queryset):
    ids = []
    for c in queryset:
        ids.append(c.id)
    return services.export_subscriptions(ids, 'csv')
export_confirmed_subscriptions_csv.short_description = "Export confirmed subscriptions of selected course as CSV"

def export_confirmed_subscriptions_xlsx(modeladmin, request, queryset):
    ids = []
    for c in queryset:
        ids.append(c.id)
    return services.export_subscriptions(ids, 'xlsx')
export_confirmed_subscriptions_xlsx.short_description = "Export confirmed subscriptions of selected course as XLSX"
