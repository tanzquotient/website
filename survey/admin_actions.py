from django.contrib import admin
from django.http import HttpResponse

from django.utils import timezone

from . import services


@admin.action(description="Export Excel")
def export_surveys_xlsx(modeladmin, request, queryset) -> HttpResponse:
    return services.export_surveys(queryset.all())


@admin.action(description="Let selected survey instances expire now")
def let_url_expire_now(modeladmin, request, queryset) -> None:
    queryset.update(url_expire_date=timezone.now())


@admin.action(description="Make a copy of selected surveys (survey instances are not copied)")
def copy_survey(modeladmin, request, queryset) -> None:
    for s in queryset:
        s.copy()
