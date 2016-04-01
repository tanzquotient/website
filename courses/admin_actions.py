from django.contrib import admin

from courses.models import *

import services

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


def display(modeladmin, request, queryset):
    queryset.update(display=True)


display.short_description = "Set displayed"


def undisplay(modeladmin, request, queryset):
    queryset.update(display=False)


undisplay.short_description = "Set undisplayed"


def activate(modeladmin, request, queryset):
    queryset.update(active=True)


activate.short_description = "Activate"


def deactivate(modeladmin, request, queryset):
    queryset.update(active=False)


deactivate.short_description = "Deactivate"


def copy_courses(modeladmin, request, queryset):
    for c in queryset:
        services.copy_course(c)


copy_courses.short_description = "Create copy of courses for the subsequent offering"


def confirm_subscriptions(modeladmin, request, queryset):
    # this is directly executed with database query, does not trigger signals!
    queryset.update(confirmed=True)

    # manually send confirmation mails
    services.confirm_subscriptions(queryset)


confirm_subscriptions.short_description = "Confirm selected subscriptions"


def reject_subscriptions(modeladmin, request, queryset):
    # this is directly executed with database query, does not trigger signals!
    queryset.update(rejected=True)

    # manually send confirmation mails
    services.reject_subscriptions(queryset)


reject_subscriptions.short_description = "Reject selected subscriptions"


def match_partners(modeladmin, request, queryset):
    services.match_partners(queryset)


match_partners.short_description = "Match partners (chronologically, body height optimal)"


def set_subscriptions_as_payed(modeladmin, request, queryset):
    queryset.update(payed=True)


set_subscriptions_as_payed.short_description = "Set selected subscriptions as payed"


def export_confirmed_subscriptions_csv(modeladmin, request, queryset):
    ids = []
    for c in queryset:
        ids.append(c.id)
    return services.export_subscriptions(ids, 'csv')


export_confirmed_subscriptions_csv.short_description = "Export confirmed subscriptions of selected courses as CSV"


def export_confirmed_subscriptions_csv_google(modeladmin, request, queryset):
    ids = []
    for c in queryset:
        ids.append(c.id)
    return services.export_subscriptions(ids, 'csv_google')


export_confirmed_subscriptions_csv_google.short_description = "Export confirmed subscriptions of selected courses as Google Contacts readable CSV"


def export_confirmed_subscriptions_xlsx(modeladmin, request, queryset):
    ids = []
    for c in queryset:
        ids.append(c.id)
    return services.export_subscriptions(ids, 'xlsx')


export_confirmed_subscriptions_xlsx.short_description = "Export confirmed subscriptions of selected courses as XLSX"
