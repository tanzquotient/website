from django.db import models
from django.conf import settings
from courses.models import Subscribe, Course
from post_office.models import Email
from django.core.exceptions import ValidationError


class Payment(models.Model):
    """
    A Payment is a any registered payment on the account, regardless of its purpose.
    """

    class State:
        NEW = 'new'
        MANUAL = 'manual'
        MATCHED = 'matched'
        PROCESSED = 'processed'

        CHOICES = ((NEW, 'new'), (MANUAL, 'manual'), (MATCHED, 'matched'), (PROCESSED, 'processed'))

    class Type:
        SUBSCRIPTION_PAYMENT = 'subscription_payment'
        SUBSCRIPTION_PAYMENT_TO_REIMBURSE = 'subscription_payment_to_reimburse'
        COURSE_PAYMENT_TRANSFER = 'course_payment_transfer'
        IRRELEVANT = 'irrelevant'
        UNKNOWN = 'unknown'

        CHOICES = ((SUBSCRIPTION_PAYMENT, 'subscription payment'),
                   (SUBSCRIPTION_PAYMENT_TO_REIMBURSE, 'subscription payment (to reimburse)'),
                   (COURSE_PAYMENT_TRANSFER, 'course payment transfer'), (IRRELEVANT, 'irrelevant'),
                   (UNKNOWN, 'unknown'))

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

    def courses(self):
        return [subscription.course for subscription in self.subscriptions.all()]

    def list_subscriptions(self):
        return [subscription_payment.subscription.__str__() for subscription_payment in
                SubscriptionPayment.objects.filter(payment=self).all()]

    def subscription_payments_amount_sum(self):
        sum = 0
        for sp in self.subscription_payments.all():
            sum += sp.amount
        return sum


class SubscriptionPayment(models.Model):
    """
    A Subscription Payment is a matched intermediate object.
    It also registers how much of the original amount of the associated payment is actually utilized
    """
    payment = models.ForeignKey(Payment, related_name='subscription_payments')
    subscription = models.ForeignKey(Subscribe, related_name='subscription_payments')
    amount = models.FloatField()

    def balance(self):
        return self.amount - self.subscription.get_price_to_pay()

    def clean(self):
        # Don't allow larger amount then available amount of payment
        if self.amount and (self.amount > self.payment.amount):
            raise ValidationError('The available payment amount is not sufficient to allow the association of {}.'.format(self.amount))


class CoursePayment(models.Model):
    """
    A Course Payment is a matched intermediate object.
    """
    payment = models.ForeignKey(Payment, related_name='course_payments')
    course = models.ForeignKey(Course, related_name='course_payments')
    amount = models.FloatField()


class PaymentReminder(models.Model):
    subscription = models.ForeignKey(Subscribe, related_name='payment_reminders')
    date = models.DateField(blank=False, null=False, auto_now_add=True)
    date.help_text = "The date when the reminder mail was sent to the subscriber."
    mail = models.ForeignKey(Email, blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return "({}) reminded of missing payment at {}".format(self.subscription, self.date)
