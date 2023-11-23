from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render

from survey.models import SurveyInstance


@login_required()
def overview_as_teacher(request: HttpRequest) -> HttpResponse:
    if not request.user.profile.is_teacher():
        raise PermissionDenied

    courses = list(
        {
            survey_instance.course
            for survey_instance in SurveyInstance.objects.filter(
                course__teaching__teacher=request.user, survey__teachers_allowed=True
            ).prefetch_related("course__offering", "course__type")
        }
    )
    courses.sort(key=lambda course: course.get_last_lesson_date())
    return render(
        request, "survey/overview_as_teacher.html", context=dict(courses=courses)
    )
