from typing import Iterable

from django.http import HttpResponse

from courses.utils import export
from survey.models import Survey


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
