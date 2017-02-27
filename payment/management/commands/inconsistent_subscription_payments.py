from django.core.management.base import BaseCommand

from payment.models import *
from courses.models import *

import logging

log = logging.getLogger('tq')


class Command(BaseCommand):
    help = 'lists payments with inconsistent state (e.g. payment method not set)'

    def handle(self, *args, **options):
        msg_method = []
        msg_amount = []
        for p in Payment.objects.all():
            if p.state == Payment.State.PROCESSED and p.type == Payment.Type.SUBSCRIPTION_PAYMENT:
                for sp in p.subscription_payments.all():
                    s = sp.subscription
                    if not s.paymentmethod:
                        msg_method.append("{} - {} - {}".format(s.id, s.usi, s))
                    if sp.balance() != 0:
                        msg_amount.append(
                            "{} - {} - {} - balance: {}".format(s.id, s.usi, s,
                                                                sp.balance()))
        # Output
        print('payment method not set')
        for msg in msg_method:
            print(msg)
        print('amount of subscription and linked subscription payment not equal:')
        for msg in msg_amount:
            print(msg)
