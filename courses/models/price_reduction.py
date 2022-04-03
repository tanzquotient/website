from __future__ import annotations

from django.db.models import Model, ForeignKey, DecimalField, CharField, DateTimeField, PROTECT, CASCADE

from courses.models import PaymentMethod


class PriceReduction(Model):
    subscription = ForeignKey('Subscribe', related_name='price_reductions', on_delete=CASCADE)
    amount = DecimalField(decimal_places=2, max_digits=6)
    used_voucher = ForeignKey('Voucher', related_name='price_reductions', blank=True, null=True, on_delete=PROTECT)
    comment = CharField(max_length=128, blank=True, null=True)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None) -> None:
        super().save(force_insert, force_update, using, update_fields)
        if self.subscription.open_amount() == 0 and not self.subscription.paid():
            self.subscription.mark_as_paid(PaymentMethod.PRICE_REDUCTION)

    def __str__(self) -> str:
        return f"{self.amount}"
