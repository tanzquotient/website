from payment.payment_processor import PaymentProcessor
from payment.models import Payment


def process_payments(modeladmin, request, queryset):
    PaymentProcessor().process_payments(queryset)


process_payments.short_description = "Process selected payments"


def match_payments(modeladmin, request, queryset):
    PaymentProcessor().match_payments(queryset)


match_payments.short_description = "Only match selected payments"


def finalize_payments(modeladmin, request, queryset):
    PaymentProcessor().finalize_payments(queryset)


finalize_payments.short_description = "Finalize selected payments (set payment method and send payment confirmation)"


def check_balance(modeladmin, request, queryset):
    PaymentProcessor().check_balance(queryset)


check_balance.short_description = "Check balance and if ok mark selected payments as matched (will be finalized automatically)"


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
        
def mark_archive(modeladmin, request, queryset):
    for payment in queryset:
        payment.state = Payment.State.ARCHIVE
        payment.save()    


mark_archive.short_description = "Archive selected payments"
