import hashlib, zlib
import cPickle as pickle
import urllib
from django.core.urlresolvers import reverse
from django.utils.encoding import escape_uri_path

from tq_website import settings as my_settings

from post_office import mail, models as post_office_models
import logging

log = logging.getLogger('tq')

SALT = "lkd$lrn&"


def encode_data(data):
    """Turn `data` into a hash and an encoded string, suitable for use with `decode_data`."""
    text = zlib.compress(pickle.dumps(data, 0)).encode('base64').replace('\n', '')
    checksum = hashlib.md5(SALT + text).hexdigest()[:12]
    return text, checksum


def decode_data(text, checksum):
    """The inverse of `encode_data`."""
    text = urllib.unquote(text)
    c = hashlib.md5(SALT + text).hexdigest()[:12]
    if c != checksum:
        raise Exception("Bad hash!")
    data = pickle.loads(zlib.decompress(text.decode('base64')))
    return data


def create_url(survey_inst):
    return u"{}?t={}&c={}".format(reverse('survey:survey_invitation'), escape_uri_path(survey_inst.url_text),
                                  escape_uri_path(survey_inst.url_checksum))


def send_invitation(survey_inst):
    if survey_inst.invitation_sent:
        return False

    context = {
        'first_name': survey_inst.user.first_name,
        'last_name': survey_inst.user.last_name,
        'course': survey_inst.course.type.name,
        'offering': survey_inst.course.offering.name,
        'expires': survey_inst.url_expire_date,
        'url': create_url(survey_inst),
    }

    template = 'survey_invitation'

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
            [email, my_settings.EMAIL_HOST_USER],
            my_settings.DEFAULT_FROM_EMAIL,
            template=template,
            context=context,
        )
        return True
    except post_office_models.EmailTemplate.DoesNotExist as e:
        log.error("Email Template missing with name: {}".format(template))
        return False
