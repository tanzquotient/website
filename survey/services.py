from typing import Iterable

from django.contrib.auth.models import User
from django.http import HttpResponse

from courses.utils import export
from survey.models import Survey, SurveyInstance


def export_surveys(surveys: Iterable[Survey]) -> HttpResponse:

    export_format = "excel"
    export_data = []

    for survey in surveys:
        data = []

        questions = []
        for group in survey.questiongroup_set.all():
            questions += list(group.question_set.all())

        columns = ["User"] + [question.name for question in questions]
        data.append(columns)

        for instance in survey.survey_instances.exclude(last_update=None):
            # only take the newest answer if multiple submissions
            answers = instance.answers.order_by('-id')
            row = [instance.user.username]
            for question in questions:
                answers_for_question = answers.filter(question=question)
                answer = None
                if answers_for_question.count() > 0:
                    answer = answers_for_question.first().value
                row.append(answer)

            data.append(row)

        export_data.append({'name': survey.name, 'data': data})

    return export(export_format, title="Survey results", data=export_data, multiple=True)


def get_or_create_survey_instance(survey: Survey, user: User) -> SurveyInstance:
    instances_query = SurveyInstance.objects.filter(user=user, survey=survey)
    if instances_query.exists():
        instances = list(instances_query.order_by("-date").all())
        for instance in instances:
            if not instance.is_completed():
                return instance  # Return not-completed instance first
        return instances[0]  # Return any completed instance

    survey_instance = SurveyInstance(survey=survey, user=user)
    survey_instance.save()
    return survey_instance
