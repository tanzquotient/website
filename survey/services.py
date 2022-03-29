from typing import Iterable

from django.contrib.auth.models import User
from django.http import HttpResponse

from courses.utils import export
from survey.models import Survey, SurveyInstance


def export_surveys(surveys: Iterable[Survey]) -> HttpResponse:

    export_format = "excel"
    export_data = {}

    multiple_surveys = len(list(surveys)) > 1

    for survey in surveys:

        questions = []
        for group in survey.questiongroup_set.all():
            questions += list(group.question_set.all())

        header = ["User", "Course"] + [question.name for question in questions]
        key_prefix = f"{survey.name} - " if multiple_surveys else ""
        key_all = f"{key_prefix}All"
        if key_all not in export_data:
            export_data[key_all] = [header]

        for instance in survey.survey_instances.filter(is_completed=True)\
                .prefetch_related('answers', 'answers__question').all():
            if not instance.has_answers():
                instance.is_completed = False
                instance.save()
                continue

            key = f"{key_prefix}{instance.course.name}"
            if key not in export_data:
                export_data[key] = [header]

            # only take the newest answer if multiple submissions
            answers = instance.answers.order_by('-id')
            row = [
                f"{instance.user.first_name} {instance.user.last_name}" if instance.user else "",
                instance.course.name if instance.course else ""
            ]
            for question in questions:
                answers_for_question = answers.filter(question=question)
                answer = None
                if answers_for_question.count() > 0:
                    answer = answers_for_question.first().value
                row.append(answer)

            export_data[key].append(row)
            export_data[key_all].append(row)

    return export(export_format=export_format,
                  title="Survey results",
                  data=[dict(name=k, data=v) for k, v in export_data.items()],
                  multiple=True)


def get_or_create_survey_instance(survey: Survey, user: User) -> SurveyInstance:
    instances_query = SurveyInstance.objects.filter(user=user, survey=survey)
    if instances_query.exists():
        instances = list(instances_query.order_by("-date").all())
        for instance in instances:
            if not instance.has_answers():
                return instance  # Return not-completed instance first
        return instances[0]  # Return any completed instance

    survey_instance = SurveyInstance(survey=survey, user=user)
    survey_instance.save()
    return survey_instance
