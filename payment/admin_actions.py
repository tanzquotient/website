from payment.payment_processor import PaymentProcessor
from payment.models import Payment

def process_payments(modeladmin, request, queryset):
    payment_processor = PaymentProcessor()
    return payment_processor.match_payments(queryset)


process_payments.short_description = "Process selected payments"

def mark_payments_as_new(modeladmin, request, queryset):
    for payment in queryset:
        payment.state = Payment.State.NEW
        payment.save()


mark_payments_as_new.short_description = "Mark selected payments as new (will be reprocessed)"