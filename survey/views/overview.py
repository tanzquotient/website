from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from ..models import Survey


@staff_member_required
def overview(request: HttpRequest) -> HttpResponse:
    surveys = (
        Survey.objects.prefetch_related(
            "translations",
            "survey_instances__course",
            "survey_instances__course__offering",
        )
        .order_by("-id")
        .all()
    )
    context = dict(
        surveys=surveys,
    )
    return render(request, "survey/overview.html", context=context)
