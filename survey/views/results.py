from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, get_object_or_404

from courses.models import Offering, Course
from .changed_answers import show_or_hide_answer_on_post
from ..models import Survey


@login_required
def results(request: HttpRequest, survey_id: int) -> HttpResponse:
    get_object_or_404(Survey, id=survey_id)

    show_or_hide_answer_on_post(request)

    selected_course = None
    if "course_id" in request.GET and request.GET["course_id"]:
        selected_course = get_object_or_404(Course, id=request.GET["course_id"])

    if not request.user.is_staff and not (
        selected_course and request.user in selected_course.get_teachers()
    ):
        raise PermissionDenied

    survey = (
        Survey.objects.filter(id=survey_id)
        .prefetch_related(
            "questiongroup_set",
            "questiongroup_set__translations",
            "questiongroup_set__question_set",
            "questiongroup_set__question_set__translations",
            "questiongroup_set__question_set__scale",
            "questiongroup_set__question_set__scale__translations",
            "questiongroup_set__question_set__choice_set",
            "questiongroup_set__question_set__choice_set__translations",
            "questiongroup_set__question_set__answers__survey_instance__course__room",
            "questiongroup_set__question_set__answers__survey_instance__course__type",
            "questiongroup_set__question_set__answers__survey_instance__course__teaching__teacher__profile",
        )
        .first()
    )

    offerings = (
        Offering.objects.filter(course__survey_instances__survey=survey)
        .distinct()
        .order_by("name")
        .all()
    )

    selected_offering = None

    if selected_course:
        selected_offering = selected_course.offering
    elif "offering_id" in request.GET and request.GET["offering_id"]:
        selected_offering = get_object_or_404(Offering, id=request.GET["offering_id"])
    elif offerings.count() == 1:
        selected_offering = offerings.first()

    courses = []
    if selected_offering:
        courses = (
            selected_offering.course_set.filter(survey_instances__survey=survey)
            .distinct()
            .order_by("name")
            .all()
        )

    survey_instances = survey.survey_instances
    if selected_course:
        survey_instances = survey_instances.filter(course=selected_course)
    elif selected_offering:
        survey_instances = survey_instances.filter(course__offering=selected_offering)

    context = dict(
        survey=survey,
        offerings=offerings,
        courses=courses,
        selected_offering=selected_offering,
        selected_course=selected_course,
        survey_instances=survey_instances,
        answers_count=survey_instances.filter(is_completed=True).count(),
    )
    return render(request, "survey/results.html", context=context)
