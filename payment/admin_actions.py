from payment_processor import PaymentProcessor

def process_payments(modeladmin, request, queryset):
    payment_processor = PaymentProcessor()
    return payment_processor.match_payments(queryset)


process_payments.short_description = "Process selected payments"
