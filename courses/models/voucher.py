from __future__ import annotations

import datetime
from decimal import Decimal
from typing import Optional

from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import (
    Model,
    ForeignKey,
    IntegerField,
    CharField,
    DateField,
    BooleanField,
    FileField,
    CheckConstraint,
    Q,
    PROTECT,
)
from django.utils.translation import gettext_lazy as _
from reversion import revisions as reversion

from courses.models import Subscribe
from utils import CodeGenerator


def generate_key() -> str:
    voucher_key = CodeGenerator.short_uuid_without_ambiguous_characters()
    return (
        voucher_key
        if not Voucher.objects.filter(key=voucher_key).exists()
        else generate_key()
    )


@reversion.register()
class Voucher(Model):
    purpose = ForeignKey("VoucherPurpose", related_name="vouchers", on_delete=PROTECT)
    amount = IntegerField(
        blank=True, null=True, help_text=_("Value of the voucher in CHF.")
    )
    percentage = IntegerField(
        blank=True, null=True, help_text=_("Reduction in percent (0-100).")
    )
    key = CharField(
        max_length=8,
        unique=True,
        default=generate_key,
        help_text=_("Used to redeem voucher."),
    )
    issued = DateField(auto_now_add=True)
    expires = DateField(
        blank=True, null=True, help_text=_("If not set, the voucher will not expire.")
    )
    used = BooleanField(default=False)
    pdf_file = FileField(
        upload_to="voucher/", null=True, blank=True, help_text=_("Will be generated.")
    )
    subscription = ForeignKey(
        "Subscribe",
        blank=True,
        null=True,
        on_delete=PROTECT,
        help_text=_("The voucher was applied for this subscription."),
    )
    comment = CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text=_("Optional description of the purpose of the voucher."),
    )
    sent_to = ForeignKey(
        to=User,
        related_name="voucher",
        on_delete=PROTECT,
        blank=True,
        null=True,
        help_text=_("User that the voucher was sent to."),
    )

    class Meta:
        constraints = [
            CheckConstraint(
                name="percentage is null or between 0 and 100",
                condition=(
                    Q(percentage__isnull=True)
                    | (Q(percentage__gte=0) & Q(percentage__lte=100))
                ),
            ),
            CheckConstraint(
                name="amount is null or non-negative",
                condition=(Q(amount__isnull=True) | Q(amount__gte=0)),
            ),
            CheckConstraint(
                name="either amount or percentage set (not both",
                condition=(
                    Q(amount__isnull=False)
                    & Q(amount__gt=0)
                    & (Q(percentage__isnull=True) | Q(percentage=0))
                )
                | (
                    Q(percentage__isnull=False)
                    & Q(percentage__gt=0)
                    & (Q(amount__isnull=True) | Q(amount=0))
                ),
            ),
        ]
        ordering = ["-issued", "-expires"]

    def save(self, *args, **kwargs) -> None:
        if not self.issued:
            self.issued = datetime.date.today()
        from payment.utils import generate_voucher_pdf

        pdf_file = generate_voucher_pdf(voucher=self)
        self.pdf_file.save(pdf_file.name, pdf_file, save=False)
        super().save(*args, **kwargs)

    def apply_to(
        self, subscription: Subscribe, user: User
    ) -> tuple[bool, Optional[Voucher]]:
        with transaction.atomic():
            locked_voucher = Voucher.objects.select_for_update().get(pk=self.pk)
            if locked_voucher.used:
                subscription.generate_price_to_pay()
                return subscription.paid(), None

            locked_subscription = Subscribe.objects.select_for_update().get(
                pk=subscription.pk
            )

            locked_subscription.generate_price_to_pay()

            reduction_amount = locked_voucher.get_reduction_amount(
                base_value=locked_subscription.get_price_to_pay()
            )
            open_amount_before = locked_subscription.open_amount()

            voucher_for_remainder = None
            if open_amount_before < reduction_amount:
                remainder = reduction_amount - open_amount_before
                reduction_amount = open_amount_before
                with reversion.create_revision():
                    comment = (
                        f"Automatically generated due to remaining value after applying"
                        f" voucher {locked_voucher.key} for {locked_subscription}"
                    )
                    voucher_for_remainder = Voucher.objects.create(
                        amount=remainder,
                        purpose=locked_voucher.purpose,
                        expires=locked_voucher.expires,
                        sent_to=user,
                        comment=comment,
                    )
                    reversion.set_user(user)
                    reversion.set_comment(comment)

            if reduction_amount > 0:
                locked_subscription.apply_price_reduction(reduction_amount, locked_voucher, user)

            locked_voucher.mark_as_used(
                locked_subscription,
                user,
                comment=f"Used to pay subscription {locked_subscription.usi}.",
            )

            return locked_subscription.paid(), voucher_for_remainder

    def get_reduction_amount(self, base_value: Decimal) -> Decimal:
        if self.percentage:  # This is a percentage voucher
            return base_value * Decimal(self.percentage) / Decimal(100)

        return Decimal(self.amount)

    def mark_as_used(
        self,
        subscription: Optional[Subscribe] = None,
        user: Optional[User] = None,
        comment: Optional[str] = None,
    ) -> None:
        with transaction.atomic(), reversion.create_revision():
            self.used = True
            self.subscription = subscription  # which subscription was paid
            self.save()
            if user and not user.is_anonymous:
                reversion.set_user(user)
            reversion.set_comment("Marked as used. " + (comment or ""))

    def value_string(self) -> str:
        if self.amount:
            return f"{self.amount} CHF"
        return f"{self.percentage}%"

    def __str__(self) -> str:
        return f"{self.key}: {self.value_string()}, issued on {self.issued}"
