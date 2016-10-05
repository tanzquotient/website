from daterange_filter.filter import DateRangeFilter

from django.contrib import admin

from payment.models import *
from payment.admin_actions import *

class SubscriptionPaymentInline(admin.TabularInline):
    model = SubscriptionPayment
    extra = 0


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'state',  'type', 'name', 'date', 'address', 'transaction_id',  'amount',
                    'amount_to_reimburse',
                    'currency_code', 'remittance_user_string']
    list_filter = ['state', 'type',  ('date', DateRangeFilter)]
    search_fields = ['id', 'name', 'address', 'transaction_id', 'iban', 'bic', 'amount',
                     'currency_code', 'remittance_user_string', 'filename']
    #inlines = [SubscriptionPaymentInline]
    actions = [process_payments, mark_payments_as_new, mark_payment_as_processed, mark_payment_as_irrelevant, mark_payment_as_course_payment]

@admin.register(SubscriptionPayment)
class SubscriptionPaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'payment', 'subscription', 'amount']
    raw_id_fields = ['payment', 'subscription']
    search_fields = ['id', 'payment', 'subscription', 'amount']



@admin.register(CoursePayment)
class CoursePaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'payment', 'course', 'amount']
    raw_id_fields = ['payment', 'course']
    search_fields = ['id', 'payment', 'course', 'amount']