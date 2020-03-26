import hashlib

from courses.utils import export

try:
    import pickle
except ImportError:
    import cPickle as pickle

from django.conf import settings
from django.contrib.sites.models import Site
from django.urls import reverse
from django.http import HttpResponse
from django.utils.encoding import escape_uri_path

from tq_website import settings as my_settings

from post_office import mail, models as post_office_models
import logging

from survey.models import Answer
from courses.models import Course

from django.utils import translation

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


def create_url(survey_inst):
    id_str, c = encode_id(survey_inst.id)
    return"{}?id={}&c={}".format(reverse('survey:survey_invitation'), escape_uri_path(id_str),
                                   escape_uri_path(c))


def create_full_url(survey_inst):
    return"https://{}{}".format(Site.objects.get(id=settings.SITE_ID).domain, create_url(survey_inst))


def send_invitation(survey_inst):
    if survey_inst.invitation_sent:
        return False

    lang = translation.get_language()
    translation.activate('de')
    url_de = create_full_url(survey_inst)
    translation.activate('en')
    url_en = create_full_url(survey_inst)
    translation.activate(lang)

    context = {
        'first_name': survey_inst.user.first_name,
        'last_name': survey_inst.user.last_name,
        'course': survey_inst.course.type.name,
        'offering': survey_inst.course.offering.name,
        'expires': survey_inst.url_expire_date,
        'url': url_de,
        'url_en': url_en,
        'url_de': url_de,
    }

    template = 'survey_invitation'
    if survey_inst.email_template:
        template = survey_inst.email_template

    if _email_helper(survey_inst.user.email, template, context):
        survey_inst.invitation_sent = True
        survey_inst.save()
        return True
    else:
        return False


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

        columns = [question.name for question in questions]
        data.append(columns)

        for instance in survey.survey_instances.exclude(last_update=None):
            # only take the newest answer if multiple submissions
            answers = instance.answers.order_by('-id')
            row = []
            for question in questions:
                answers_for_question = answers.filter(question=question)
                answer = answers_for_question.first() if answers_for_question.count() > 0 else None
                row.append(answer)

            data.append(row)


        export_data.append({'name': survey.name, 'data': data})


    return export(export_format, title="Survey results", data=export_data, multiple=True)
