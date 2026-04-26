import logging
from typing import Iterable, Optional

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.db import transaction

from courses.models import Course, Offering
from utils import export
from survey.models import Survey, SurveyInstance
from email_system.services import send_all_emails
from post_office.models import EmailTemplate
from tq_website import settings

log = logging.getLogger("tq")


def export_surveys(
    surveys: Iterable[Survey],
    offering: Optional[Offering] = None,
    course: Optional[Course] = None,
    export_format: str = None,
    anonymize: bool = True,
) -> HttpResponse:
    export_data = {}
    export_format = export_format or "excel"

    multiple_surveys = len(list(surveys)) > 1

    for survey in surveys:
        questions = []
        for group in survey.questiongroup_set.all():
            questions += list(group.question_set.all())

        header = ["User", "Email", "Course"] + [question.name for question in questions]
        key_prefix = f"{survey.name} - " if multiple_surveys else ""
        key_all = f"{key_prefix}All"
        if key_all not in export_data:
            export_data[key_all] = [header]

        survey_instances = survey.survey_instances.filter(is_completed=True)
        if offering:
            survey_instances = survey_instances.filter(course__offering=offering)
        if course:
            survey_instances = survey_instances.filter(course=course)

        for instance in survey_instances.prefetch_related(
            "answers", "answers__question"
        ).all():
            if not instance.has_answers():
                instance.is_completed = False
                instance.save()
                continue

            course_name = instance.course.name if instance.course else ""
            key = f"{key_prefix}{course_name}"
            if key not in export_data:
                export_data[key] = [header]

            # only take the newest answer if multiple submissions
            answers = instance.answers.order_by("-id")
            row = [
                (
                    "anonymized"
                    if anonymize
                    else (
                        f"{instance.user.first_name} {instance.user.last_name}"
                        if instance.user
                        else ""
                    )
                ),
                (
                    "anonymized"
                    if anonymize
                    else f"{instance.user.email}" if instance.user else ""
                ),
                course_name,
            ]
            for question in questions:
                answers_for_question = answers.filter(question=question)
                answer = None
                if answers_for_question.count() > 0:
                    answer = answers_for_question.first().value
                row.append(answer)

            export_data[key].append(row)
            export_data[key_all].append(row)

    if len(export_data.keys()) == 2:  # All + specific (but they are identical
        multiple = False
        data = list(export_data.values())[0]
    else:
        multiple = True
        data = [dict(name=k, data=v) for k, v in export_data.items()]

    return export(
        export_format=export_format,
        title="Survey results",
        data=data,
        multiple=multiple,
    )


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


def send_course_surveys() -> None:
    email_template = EmailTemplate.objects.get(name="survey_invitation")
    BATCH_SIZE = 100
    emails = []
    total_sent = 0

    # get all offerings with a survey assigned
    offerings = Offering.objects.select_for_update().filter(
        survey__isnull=False,
    )

    with transaction.atomic():
        for offering in offerings:
            # get all courses in the offering
            courses = Course.objects.filter(
                offering=offering,
                cancelled=False,
            )
            for course in courses:

                # check if the course is over
                if not course.is_over():
                    continue

                already_invited_user_ids = set(
                    SurveyInstance.objects.filter(
                        course=course,
                        survey=offering.survey,
                    ).values_list("user_id", flat=True)
                )

                recipients = (
                    User.objects.filter(
                        pk__in=course.participatory().values_list("user_id", flat=True)
                    )
                    .exclude(pk__in=already_invited_user_ids)
                )

                for recipient in recipients.iterator(chunk_size=200):
                    # create a survey instance
                    survey_instance = SurveyInstance.objects.create(
                        survey=offering.survey,
                        email_template=email_template,
                        course=course,
                        user=recipient,
                    )

                    context = {
                        "first_name": recipient.first_name,
                        "last_name": recipient.last_name,
                        "course": course.type.title,
                        "offering": course.offering.name,
                        "offering_title_en": course.offering.safe_translation_getter(
                            "title", language_code="en"
                        ),
                        "offering_title_de": course.offering.safe_translation_getter(
                            "title", language_code="de"
                        ),
                        "survey_url": survey_instance.create_full_url(),
                        "survey_expiration": survey_instance.url_expire_date,
                    }
                    log.info(
                        f"Will send survey invitation to {recipient.username} for course {course.type.title} in offering {course.offering.name}"
                    )

                    emails.append(
                        dict(
                            to=recipient.email,
                            reply_to=settings.EMAIL_ADDRESS_DANCE_ADMIN,
                            template=email_template,
                            context=context,
                        )
                    )

                    if len(emails) >= BATCH_SIZE:
                        send_all_emails(emails)
                        total_sent += len(emails)
                        emails = []

        if emails:
            send_all_emails(emails)
            total_sent += len(emails)
        log.info(f"Sent {total_sent} survey emails")
