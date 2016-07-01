from django.db import models
from django.conf import settings
from courses.models import Subscribe


class Payment(models.Model):
    """
    A Payment is a any registered payment on the account, regardless of its purpose.
    """

    class State:
        NEW = 'new'
        MANUAL = 'manual'
        PROCESSED = 'processed'

        CHOICES = ((NEW, u'new'), (MANUAL, u'manual'), (PROCESSED, u'processed'))

    class Type:
        SUBSCRIPTION_PAYMENT = 'subscription_payment'
        SUBSCRIPTION_PAYMENT_TO_REIMBURSE = 'subscription_payment_to_reimburse'
        COURSE_PAYMENT_TRANSFER = 'course_payment_transfer'
        IRRELEVANT = 'irrelevant'
        UNKNOWN = 'unknown'

        CHOICES = ((SUBSCRIPTION_PAYMENT, u'subscription payment'),
                   (SUBSCRIPTION_PAYMENT_TO_REIMBURSE, u'subscription payment (to reimburse)'),
                   (COURSE_PAYMENT_TRANSFER, u'course payment transfer'), (IRRELEVANT, u'irrelevant'),
                   (UNKNOWN, u'unknown'))

    name = models.CharField(max_length=200, blank=True, null=True)
    date = models.DateTimeField()
    address = models.TextField(null=True, blank=True)
    iban = models.CharField(max_length=34, null=True, blank=True)
    bic = models.CharField(max_length=11, null=True, blank=True)
    transaction_id = models.CharField(max_length=100)
    amount = models.FloatField()
    amount_to_reimburse = models.FloatField(blank=True, default=0)
    currency_code = models.CharField(max_length=3)
    remittance_user_string = models.CharField(max_length=300)
    state = models.CharField(choices=State.CHOICES, max_length=50, default=State.NEW)
    type = models.CharField(verbose_name='type (detected)', choices=Type.CHOICES, max_length=50, default=Type.UNKNOWN,
                            help_text="The type is auto-detected when the state is NEW, otherwise the detector will not touch this field anymore.")
    subscriptions = models.ManyToManyField(Subscribe, blank=True, through='SubscriptionPayment')
    filename = models.CharField(max_length=300)

    def __str__(self):
        return "Payment of {0} by {1}".format(self.amount, self.name)

    def __unicode__(self):
        return u"Payment of {0} by {1}".format(self.amount, self.name)


class SubscriptionPayment(models.Model):
    """
    A Subscription Payment is a matched intermediate object.
    It also registers how much of the original amount of the associated payment is actually utilized
    """
    payment = models.ForeignKey(Payment, related_name='subscription_payments')
    subscription = models.ForeignKey(Subscribe, related_name='subscription_payments')
    amount = models.FloatField()
