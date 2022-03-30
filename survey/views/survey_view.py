import logging
from collections import defaultdict
from datetime import datetime
from typing import Optional

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from ..models import Survey, Answer, SurveyInstance
from ..services import get_or_create_survey_instance
from tq_website import settings


log = logging.getLogger('tq')


def _get_survey_instance(url_key: str):
    get_object_or_404(SurveyInstance, url_key=url_key)
    return SurveyInstance.objects.filter(url_key=url_key) \
        .prefetch_related('survey__questiongroup_set',
                          'survey__questiongroup_set__question_set',
                          'survey__questiongroup_set__question_set__scale').get()


def survey_view(request, survey_id: int, url_key: Optional[str] = None) -> HttpResponse:

    survey = get_object_or_404(Survey, pk=survey_id)

    # Get survey instance
    if url_key:
        survey_instance = _get_survey_instance(url_key)
    else:
        if not request.user.is_authenticated:
            return redirect(f"{settings.LOGIN_URL}?next={request.path}")
        survey_instance = get_or_create_survey_instance(survey, request.user)

    if survey_instance.has_answers():
        context = {'already_completed': True, 'survey_instance': survey_instance}
        return render(request, "survey/survey_done.html", context)

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

        if survey_instance.has_answers():
            survey_instance.is_completed = True
            survey_instance.last_update = datetime.now()
            survey_instance.save()

            return render(request, "survey/survey_done.html", {'survey_instance': survey_instance})

    return render(request, "survey/survey.html", {'survey_instance': survey_instance})
