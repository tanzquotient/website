import logging
from collections import defaultdict
from typing import Optional

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect

from tq_website import settings
from . import models
from .models import Survey, SurveyInstance, Answer

log = logging.getLogger('tq')


# Create your views here.


def _get_survey_instance(url_key: str):
    get_object_or_404(models.SurveyInstance, url_key=url_key)
    return models.SurveyInstance.objects.filter(url_key=url_key) \
        .prefetch_related('survey__questiongroup_set',
                          'survey__questiongroup_set__question_set',
                          'survey__questiongroup_set__question_set__scale').get()


def survey_view(request, survey_id: int, url_key: Optional[str] = None) -> HttpResponse:

    survey = get_object_or_404(Survey, pk=survey_id)

    # TODO: Check if user filled out survey already

    if url_key:
        survey_instance = _get_survey_instance(url_key)

    else:
        if not request.user.is_authenticated:
            return redirect(f"{settings.LOGIN_URL}?next={request.path}")

        survey_instance = SurveyInstance(survey=survey, user=request.user)
        survey_instance.save()

    if request.method == 'POST':
        answers = defaultdict(list)
        for question_and_choice_id, value in request.POST.items():
            question_id = question_and_choice_id.split("-")[0]
            if question_id.isdigit() and value:
                answers[int(question_id)].append(value)

        Answer.objects.bulk_create([Answer(
            survey_instance=survey_instance,
            question_id=question_id,
            value=";".join(values)
        ) for question_id, values in answers.items()])

        return render(request, "survey/survey_done.html")

    return render(request, "survey/survey.html", {'survey_instance': survey_instance})
