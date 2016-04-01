import hashlib, zlib
import cPickle as pickle
import urllib
from django.core.urlresolvers import reverse
from django.utils.encoding import escape_uri_path

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
    return u"{}?t={}&c={}".format(reverse('survey_invitation'), escape_uri_path(survey_inst.url_text), escape_uri_path(survey_inst.url_checksum))
