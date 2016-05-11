from django.contrib import admin

from payment.models import *


# Register your models here.
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'date', 'address', 'iban', 'bic', 'amount', 'currency_code', 'remittance_user_string', 'state', 'subscription', 'filename']


# Register your models here.
admin.site.register(Payment, PaymentAdmin)
