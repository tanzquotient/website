from django.contrib import admin

from courses.filters import *
from payment.admin_actions import *
from payment.filters import *
from payment.models import *


class SubscriptionPaymentInline(admin.TabularInline):
    model = SubscriptionPayment
    extra = 0

    raw_id_fields = ['subscription']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'state', 'type', 'credit_debit', 'name', 'date', 'amount',
                    'amount_to_reimburse',
                    'currency_code', 'remittance_user_string', 'subscription_payments_amount_sum', 'list_subscriptions']
    list_filter = ['state', 'type', 'credit_debit',]
    search_fields = ['id', 'name', 'address', 'transaction_id', 'iban', 'bic', 'amount',
                     'currency_code', 'remittance_user_string', 'filename']

    inlines = [SubscriptionPaymentInline]
    actions = [process_payments, check_balance, mark_payment_as_irrelevant, mark_payment_as_course_payment, mark_archive]
    readonly_fields = ('credit_debit', 'name', 'date', 'address', 'transaction_id', 'amount', 'amount_to_reimburse',
                       'currency_code', 'remittance_user_string', 'filename', 'file', 'iban', 'bic')

@admin.register(PostfinanceFile)
class PostfinanceFileAdmin(admin.ModelAdmin):
    list_display = ['name', 'processed', 'downloaded_at']
    list_filter = ['processed']
    search_fields = ['name']
    readonly_fields = ['name', 'file', 'downloaded_at']


@admin.register(SubscriptionPayment)
class SubscriptionPaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'payment', 'subscription', 'amount', 'balance']
    raw_id_fields = ['payment', 'subscription']
    list_filter = [SubscriptionPaymentFilter]
    search_fields = ['id', 'amount']
    actions = [raise_price_to_pay]


@admin.register(CoursePayment)
class CoursePaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'payment', 'course', 'amount']
    raw_id_fields = ['payment', 'course']
    search_fields = ['id', 'payment', 'course', 'amount']


@admin.register(PaymentReminder)
class PaymentReminderAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'date')
    list_filter = (ConfirmationOfferingListFilter, ConfirmationCourseListFilter, 'date',)
    search_fields = ['subscription__course__name', 'subscription__course__type__name', 'subscription__user__email',
                     'subscription__user__first_name', 'subscription__user__last_name']

    model = PaymentReminder

    raw_id_fields = ('subscription', 'mail')
