from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, get_object_or_404

from courses.models import Offering, Course
from ..models import Survey


@staff_member_required
def overview(request: HttpRequest) -> HttpResponse:
    surveys = Survey.objects.prefetch_related(
        'translations',
        'survey_instances__course',
        'survey_instances__course__offering'
    ).order_by('-id').all()
    context = dict(
        surveys=surveys,
    )
    return render(request, "survey/overview.html", context=context)
