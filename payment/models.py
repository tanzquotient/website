from django.db import models
from django.conf import settings
from courses.models import Subscribe

# Create your models here.
class Payment(models.Model):

    class State:
        NEW = 'new'
        MATCHED = 'matched'
        MANUAL = 'manual'
        INSUFFICIENT = 'insufficient'
        REIMBURSE = 'reimburse'

        CHOICES = ((NEW, u'new'), (MATCHED, u'matched'), (MANUAL, u'manual'), (REIMBURSE, u'reimburse'), (INSUFFICIENT, u'insufficient payment'), (REIMBURSE, u'reimburse'))

    name = models.CharField(max_length=200)
    date = models.DateTimeField()
    address = models.TextField(null=True, blank=True)
    iban = models.CharField(max_length=34)
    bic = models.CharField(max_length=11, null=True, blank=True)
    amount = models.FloatField()
    currency_code = models.CharField(max_length=3)
    remittance_user_string = models.CharField(max_length=300)
    state = models.CharField(choices=State.CHOICES, max_length=20)
    subscription = models.ForeignKey(Subscribe, null=True, blank=True)
    filename = models.CharField(max_length=300)

    class Meta:
        pass

    def __str__(self):
        return "Payment of {0} by {1}".format(self.amount, self.name)

    def __unicode__(self):
        return u"Payment of {0} by {1}".format(self.amount, self.name)

