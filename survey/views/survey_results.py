from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, get_object_or_404

from ..models import Survey


@staff_member_required
def survey_results(request: HttpRequest, survey_id: int) -> HttpResponse:
    get_object_or_404(Survey, id=survey_id)
    survey = Survey.objects.filter(id=survey_id).prefetch_related(
        'questiongroup_set',
        'questiongroup_set__translations',
        'questiongroup_set__question_set',
        'questiongroup_set__question_set__translations',
        'questiongroup_set__question_set__scale',
        'questiongroup_set__question_set__scale__translations',
        'questiongroup_set__question_set__choice_set',
        'questiongroup_set__question_set__choice_set__translations',
        'questiongroup_set__question_set__answers'
    ).first()
    return render(request, "survey/results.html", context={'survey': survey})
