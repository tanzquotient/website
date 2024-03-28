from django.contrib import admin
from django.http import HttpResponse

from django.utils import timezone
from survey.models import Answer, SurveyInstance

from datetime import datetime

from . import services


@admin.action(description="Export Excel")
def export_surveys_xlsx(modeladmin, request, queryset) -> HttpResponse:
    return services.export_surveys(queryset.all())


@admin.action(description="Let selected survey instances expire now")
def let_url_expire_now(modeladmin, request, queryset) -> None:
    queryset.update(url_expire_date=timezone.now())


@admin.action(
    description="Make a copy of selected surveys (survey instances are not copied)"
)
def copy_survey(modeladmin, request, queryset) -> None:
    for s in queryset:
        s.copy()

@admin.action(description="Remove unintentional reviews")
def fix_unintentional_reviews(modeladmin, request, queryset) -> None:
    Answer.objects.filter(
        survey_instance__user__username__in=["lorenzo0", "xenia49"],
        survey_instance__last_update__gte=datetime(2024, 3, 27, 0, 0, 1),
        survey_instance__last_update__lte=datetime(2024, 3, 29, 0, 0, 1)
    ).delete()
    survey_instances = SurveyInstance.objects.filter(
        user__username__in=["lorenzo0", "xenia49"],
        last_update__gte=datetime(2024, 3, 27, 0, 0, 1),
        last_update__lte=datetime(2024, 3, 29, 0, 0, 1)
    )

    for survey_instance in survey_instances:
        survey_instance.is_completed = False
        survey_instance.save()