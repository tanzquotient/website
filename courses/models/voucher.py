import random
import string

from reversion import revisions as reversion
from django.db import models, transaction


def generate_key():
    voucher_key = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))
    while Voucher.objects.filter(key=voucher_key).count() > 0:
        voucher_key = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))
    return voucher_key


@reversion.register()
class Voucher(models.Model):

    purpose = models.ForeignKey('VoucherPurpose', related_name='vouchers', on_delete=models.PROTECT)
    percentage = models.IntegerField(default=100)
    key = models.CharField(max_length=8, unique=True, default=generate_key)
    issued = models.DateField(blank=False, null=False, auto_now_add=True)
    expires = models.DateField(blank=True, null=True)
    used = models.BooleanField(blank=False, null=False, default=False)
    pdf_file = models.FileField(upload_to='voucher/', null=True, blank=True)
    subscription = models.ForeignKey('Subscribe', blank=True, null=True, on_delete=models.PROTECT)
    subscription.help_text = 'subscription that was paid with this voucher'

    def mark_as_used(self, user=None, comment='', subscription=None):
        if not self.used:
            with transaction.atomic(), reversion.create_revision():
                self.used = True
                self.subscription = subscription  # which subscription was paid
                self.save()
                if user is not None and not user.is_anonymous():
                    reversion.set_user(user)
                reversion.set_comment('Marked as used. ' + comment)
            return True
        else:
            return False

    class Meta:
        ordering = ['-issued', '-expires']

    def __str__(self):
        return '#{} valid {} - {}'.format(self.key, self.issued, self.expires)



