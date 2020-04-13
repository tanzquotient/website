import hashlib

from courses.utils import export

try:
    import pickle
except ImportError:
    import cPickle as pickle

from tq_website import settings as my_settings

from post_office import mail, models as post_office_models
import logging

log = logging.getLogger('tq')

SALT = b"lkd$lrn&"


def calc_checksum(id_str):
    checksum = hashlib.md5()
    checksum.update(id_str.encode())
    checksum.update(SALT)
    return checksum.hexdigest()[:4].lower()


def encode_id(id):
    id_str = str(id)
    return id_str, calc_checksum(id_str)


def decode_id(id_str, checksum):
    try:
        id = int(id_str)
    except ValueError:
        log.warning(
            "The id of survey link with id='{}' and checksum='{}' could not be decoded".format(id_str, checksum))
        return False
    real_checksum = calc_checksum(id_str)  # use the string here, not the int
    if real_checksum != checksum.lower():
        log.warning(
            "The checksum of survey link with id='{}' and checksum='{}' does not match the real checksum='{}'".format(
                id_str, checksum, real_checksum))
        return False
    return int(id_str)


def _email_helper(email, template, context):
    """Sending facility. Catches errors due to not existent template."""
    try:
        mail.send(
            [email],
            my_settings.DEFAULT_FROM_EMAIL,
            template=template,
            context=context,
        )
        return True
    except post_office_models.EmailTemplate.DoesNotExist as e:
        log.error("Email Template missing with name: {}".format(template))
        return False


def export_surveys(surveys):

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
                    answer = answers_for_question.first().value()
                row.append(answer)

            data.append(row)


        export_data.append({'name': survey.name, 'data': data})


    return export(export_format, title="Survey results", data=export_data, multiple=True)
