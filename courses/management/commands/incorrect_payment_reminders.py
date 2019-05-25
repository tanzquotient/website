# -*- coding: utf-8 -*-
import logging

from django.core.management.base import BaseCommand

from courses.emailcenter import send_sorry_for_incorrect_reminder
from courses.models import *
from payment.models import *

log = logging.getLogger('tq')


class Command(BaseCommand):
    help = 'lists subscribers that were incorrectly reminded of not having paid'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sorry',
            action='store_true',
            dest='sorry',
            default=False,
            help='Send mail to say sorry',
        )

    def handle(self, *args, **options):
        log.info('run management command: {}'.format(__file__))
        print('the following subscribers where incorrectly reminded of not having paid:')
        count=0
        for pr in PaymentReminder.objects.all():
            s = pr.subscription
            if s.state in SubscribeState.PAID_STATES:
                count += 1
                print("{} - {} - {}".format(s.id, s.usi, s))
                if options['sorry']:
                    send_sorry_for_incorrect_reminder(s)
        print('TOTAL: {}'.format(count))

