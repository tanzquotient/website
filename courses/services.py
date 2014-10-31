from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _

from django.contrib import messages

from models import *

import logging
log = logging.getLogger('courses')

# Create your services here.

def subscribe(user1_data, user2_data=None):
    pass