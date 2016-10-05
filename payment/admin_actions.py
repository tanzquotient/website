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

def mark_payment_as_processed(modeladmin, request, queryset):
    short_description = "Mark selected payments as processed"
    for payment in queryset:
        payment.state = Payment.State.PROCESSED
        payment.save()

def mark_payment_as_irrelevant(modeladmin, request, queryset):
    short_description = "Mark selected payments as irrelevant"
    for payment in queryset:
        payment.state = Payment.State.PROCESSED
        payment.type = Payment.Type.IRRELEVANT
        payment.save()

def mark_payment_as_course_payment(modeladmin, request, queryset):
    short_description = "Mark selected payments as Course Payment Transfer"
    for payment in queryset:
        payment.state = Payment.State.PROCESSED
        payment.type = Payment.Type.COURSE_PAYMENT_TRANSFER
        payment.save()