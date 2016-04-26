# -*- coding: utf-8 -*-
from django.core.management.base import NoArgsCommand

from django.contrib.auth.models import User, Group, Permission

from courses import services

import logging
log = logging.getLogger('tq')

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        log.info('run management command: {}'.format(__file__))
        for user in User.objects.all():
            try:
                un = services.clean_username(user.username)
                # Note that after cleaning we must again check if username is already taken (exclude user in this check by ignore argument)
                user.username = services.find_unused_username_variant(un, ignore=user).lower()
                user.save()
                print(u'cleaned user {}'.format(user.username))  # NOTE: do not print UTF-8 symbols here
            except Exception as e:
                print(u'PROBLEM cleaning user {}: {}'.format(user.username, e))

