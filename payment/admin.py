from courses.filters import *
from payment.admin_actions import *
from payment.filters import *
from payment.models import *


class SubscriptionPaymentInline(admin.TabularInline):
    model = SubscriptionPayment
    extra = 0

    raw_id_fields = ["subscription"]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "state",
        "type",
        "credit_debit",
        "name",
        "date",
        "amount",
        "amount_to_reimburse",
        "currency_code",
        "remittance_user_string",
        "subscription_payments_amount_sum",
        "list_subscriptions",
    ]
    list_filter = ["state", "type", "credit_debit"]
    search_fields = [
        "id",
        "name",
        "address",
        "transaction_id",
        "iban",
        "bic",
        "amount",
        "currency_code",
        "remittance_user_string",
        "filename",
    ]

    inlines = [SubscriptionPaymentInline]
    show_full_result_count = False
    actions = [
        process_payments,
        check_balance,
        mark_payment_as_irrelevant,
        mark_payment_as_course_payment,
        mark_archive,
    ]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related(
                "subscription_payments__subscription__user",
                "subscription_payments__subscription__course__offering",
            )
        )

    readonly_fields = (
        "credit_debit",
        "name",
        "date",
        "address",
        "transaction_id",
        "amount",
        "amount_to_reimburse",
        "currency_code",
        "remittance_user_string",
        "filename",
        "file",
        "iban",
        "bic",
    )


@admin.register(FinanceFile)
class FinanceFileAdmin(admin.ModelAdmin):
    list_display = ["name", "processed", "created_at"]
    list_filter = ["processed"]
    search_fields = ["name"]
    readonly_fields = ["created_at"]


@admin.register(SubscriptionPayment)
class SubscriptionPaymentAdmin(admin.ModelAdmin):
    list_display = ["id", "payment", "subscription", "amount"]
    raw_id_fields = ["payment", "subscription"]
    list_filter = [SubscriptionPaymentFilter]
    search_fields = ["id", "amount"]
    actions = [raise_price_to_pay]
    show_full_result_count = False

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "payment",
                "subscription__user",
                "subscription__course__offering",
            )
        )


@admin.register(CoursePayment)
class CoursePayment(admin.ModelAdmin):
    list_display = ["id", "payment", "course", "amount"]
    raw_id_fields = ["payment", "course"]
    search_fields = ["payment__name", "course__name"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("payment", "course")


@admin.register(PayrexxGateway)
class PayrexxGatewayAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "subscription",
        "payment_method",
        "gross_amount",
        "status",
        "created_at",
        "gateway_id",
        "payrexx_transaction_id",
    ]
    list_filter = ["status", "payment_method"]
    search_fields = [
        "subscription__usi",
        "subscription__user__email",
        "subscription__user__first_name",
        "subscription__user__last_name",
        "gateway_id",
        "payrexx_transaction_id",
    ]
    raw_id_fields = ["subscription", "payment"]
    readonly_fields = [
        "gateway_id",
        "link",
        "gross_amount",
        "created_at",
        "payrexx_transaction_id",
        "payment",
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("subscription__user")


@admin.register(PaymentReminder)
class PaymentReminderAdmin(admin.ModelAdmin):
    list_display = ("subscription", "date")
    list_filter = (
        ConfirmationOfferingListFilter,
        ConfirmationCourseListFilter,
        "date",
    )
    search_fields = [
        "subscription__course__name",
        "subscription__course__type__translations__title",
        "subscription__user__email",
        "subscription__user__first_name",
        "subscription__user__last_name",
    ]

    model = PaymentReminder

    raw_id_fields = ("subscription", "mail")

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "subscription__user",
                "subscription__course__offering",
            )
        )
