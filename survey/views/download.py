from typing import Optional

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, get_object_or_404

from courses.models import Offering, Course
from ..models import Survey
from ..services import export_surveys


@staff_member_required
def download(request: HttpRequest, survey_id: int) -> HttpResponse:
    survey = get_object_or_404(Survey, id=survey_id)
    offering = None
    if "offering_id" in request.GET and request.GET["offering_id"]:
        offering = get_object_or_404(Offering, id=request.GET["offering_id"])

    course = None
    if "course_id" in request.GET and request.GET["course_id"]:
        course = get_object_or_404(Course, id=request.GET["course_id"])

    export_format = None
    if "format" in request.GET and request.GET["format"]:
        export_format = request.GET["format"]

    return export_surveys(
        [survey],
        offering,
        course,
        export_format,
        anonymize=not request.user.has_perms(
            ["survey.view_survey_instance", "survey.view_answer"]
        ),
    )
