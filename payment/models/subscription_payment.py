from django.core.exceptions import ValidationError
from django.db import models

from courses.models import Subscribe
from . import Payment

class SubscriptionPayment(models.Model):
    """
    A Subscription Payment is a matched intermediate object.
    It also registers how much of the original amount of the associated payment is actually utilized
    """
    payment = models.ForeignKey(Payment, related_name='subscription_payments', on_delete=models.PROTECT)
    subscription = models.ForeignKey(Subscribe, related_name='subscription_payments', on_delete=models.PROTECT)
    amount = models.FloatField()

    def balance(self):
        return self.amount - self.subscription.get_price_to_pay()

    def clean(self):
        # Don't allow larger amount then available amount of payment
        if self.amount and (self.amount > self.payment.amount):
            raise ValidationError(
                'The available payment amount is not sufficient to allow the association of {}.'.format(self.amount))
