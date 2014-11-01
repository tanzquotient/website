from django.contrib import admin

from courses.models import *

from services import *

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

def confirm_subscriptions(modeladmin, request, queryset):
    queryset.update(confirmed=True)
confirm_subscriptions.short_description = "Confirm selected subscriptions"

def set_subscriptions_as_payed(modeladmin, request, queryset):
    queryset.update(confirmed=True)
set_subscriptions_as_payed.short_description = "Set selected subscriptions as payed"
