# -*- coding: utf-8 -*-
from django.core.management.base import NoArgsCommand

from django.contrib.auth.models import User, Group, Permission

from courses import services
from payment.models import *
from courses.models import *

import logging

log = logging.getLogger('tq')


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        log.info('run management command: {}'.format(__file__))
        print('the following subscriptions have the incorrect state CONFIRMED eventhough there is a valid subscription payment entry:')
        for sp in SubscriptionPayment.objects.all():
            s = sp.subscription
            if s.state == Subscribe.State.CONFIRMED and s.get_price_to_pay() == sp.amount:
                print("{} - {} - {}".format(s.id, s.usi, s))
                s.state = Subscribe.State.PAYED
                s.save()

