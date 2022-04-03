from django.db import models

from .choices import *
from . import FinanceFile

from courses.models import Subscribe


class Payment(models.Model):
    """
    A Payment is a any registered payment on the account, regardless of its purpose.
    """
    name = models.CharField(max_length=200, blank=True, null=True)
    date = models.DateTimeField()
    address = models.TextField(null=True, blank=True)
    iban = models.CharField(max_length=34, null=True, blank=True)
    bic = models.CharField(max_length=11, null=True, blank=True)
    transaction_id = models.CharField(max_length=100)
    amount = models.DecimalField(decimal_places=2, max_digits=9)
    amount_to_reimburse = models.DecimalField(blank=True, default=0, decimal_places=2, max_digits=9)
    currency_code = models.CharField(max_length=3)
    remittance_user_string = models.CharField(max_length=600)
    state = models.CharField(choices=State.CHOICES, max_length=50, default=State.NEW)
    type = models.CharField(verbose_name='type (detected)', choices=Type.CHOICES, max_length=50, default=Type.UNKNOWN,
                            help_text="The type is auto-detected when the state is NEW, otherwise the detector will not touch this field anymore.")
    credit_debit = models.CharField(verbose_name='credit/debit', choices=CreditDebit.CHOICES, max_length=50, default=CreditDebit.UNKNOWN,
                                    help_text="If this transaction is a credit or a debit.")
    subscriptions = models.ManyToManyField(Subscribe, blank=True, through='SubscriptionPayment')
    filename = models.CharField(max_length=300)
    file = models.ForeignKey(to=FinanceFile, related_name='payments', null=True, blank=True, on_delete=models.SET_NULL)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return "Payment ({}) of {} by {}".format(self.credit_debit, self.amount, self.name)

    def courses(self):
        return [subscription.course for subscription in self.subscriptions.all()]

    def list_subscriptions(self):
        from . import SubscriptionPayment
        return [subscription_payment.subscription.__str__() for subscription_payment in
                SubscriptionPayment.objects.filter(payment=self).all()]

    def subscription_payments_amount_sum(self):
        sum = 0
        for sp in self.subscription_payments.all():
            sum += sp.amount
        return sum

    class Meta:
        ordering = ['-date']