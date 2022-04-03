import logging

from django.core.management.base import BaseCommand

from payment.models import *
from payment.models.choices import State, Type

log = logging.getLogger('tq')


class Command(BaseCommand):
    help = 'lists payments with inconsistent state (e.g. payment method not set)'

    def handle(self, *args, **options):
        msg_method = []
        msg_amount = []
        for p in Payment.objects.all():
            if p.state == State.PROCESSED and p.type == Type.SUBSCRIPTION_PAYMENT:
                for sp in p.subscription_payments.all():
                    s = sp.subscription
                    if not s.paymentmethod:
                        msg_method.append("{} - {} - {}".format(s.id, s.usi, s))
                    if s.sum_of_payments() != s.price_after_reductions():
                        msg_amount.append(f"{s.id} - {s.usi} - {s}: "
                                          f"price after reductions: {s.price_after_reductions()}, "
                                          f"sum of payments: {s.sum_of_payments()}")

        # Output
        print('payment method not set')
        for msg in msg_method:
            print(msg)
        print('amount of subscription and linked subscription payment not equal:')
        for msg in msg_amount:
            print(msg)
