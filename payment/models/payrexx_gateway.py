from django.db import models

from courses.models import Subscribe

from .payment import Payment


class PayrexxGateway(models.Model):
    """
    Tracks a single Payrexx hosted-checkout session from creation through webhook confirmation.
    One gateway is created per payment attempt; the link is reused on retries to avoid
    double-charging the user.
    """

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

    STATUS_CHOICES = (
        (PENDING, "Pending"),
        (COMPLETED, "Completed"),
        (FAILED, "Failed"),
        (CANCELLED, "Cancelled"),
        (EXPIRED, "Expired"),
    )

    METHOD_CARD = "card"
    METHOD_TWINT = "twint"

    METHOD_CHOICES = (
        (METHOD_CARD, "Card (Visa / Mastercard)"),
        (METHOD_TWINT, "TWINT"),
    )

    subscription = models.ForeignKey(
        Subscribe,
        related_name="payrexx_gateways",
        on_delete=models.PROTECT,
    )
    payment_method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    gateway_id = models.IntegerField(unique=True)
    link = models.URLField(max_length=500)
    gross_amount = models.DecimalField(decimal_places=2, max_digits=9)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    payrexx_transaction_id = models.IntegerField(null=True, blank=True, unique=True)
    payment = models.OneToOneField(
        Payment,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="payrexx_gateway",
    )

    def __str__(self):
        return (
            f"PayrexxGateway #{self.gateway_id} ({self.payment_method}, {self.status})"
        )

    class Meta:
        ordering = ["-created_at"]
