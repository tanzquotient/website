from django.contrib import admin

from payment.models.choices import State, Type
from payment.payment_processor import PaymentProcessor


@admin.action(description="Process selected payments")
def process_payments(modeladmin, request, queryset):
    PaymentProcessor().process_payments(queryset)


@admin.action(description="Only match selected payments")
def match_payments(modeladmin, request, queryset):
    PaymentProcessor().match_payments(queryset)


@admin.action(
    description="Finalize selected payments "
    "(set payment method and send payment confirmation)"
)
def finalize_payments(modeladmin, request, queryset):
    PaymentProcessor().finalize_payments(queryset)


@admin.action(
    description="Check balance and if ok mark selected payments as matched "
    "(will be finalized automatically)"
)
def check_balance(modeladmin, request, queryset):
    PaymentProcessor().check_balance(queryset)


@admin.action(description="Mark selected payments as irrelevant")
def mark_payment_as_irrelevant(modeladmin, request, queryset):
    for payment in queryset:
        payment.state = State.PROCESSED
        payment.type = Type.IRRELEVANT
        payment.save()


@admin.action(description="Mark selected payments as Course Payment Transfer")
def mark_payment_as_course_payment(modeladmin, request, queryset):
    for payment in queryset:
        payment.state = State.PROCESSED
        payment.type = Type.COURSE_PAYMENT_TRANSFER
        payment.save()


@admin.action(description="Archive selected payments")
def mark_archive(modeladmin, request, queryset):
    for payment in queryset:
        payment.state = State.ARCHIVE
        payment.save()
