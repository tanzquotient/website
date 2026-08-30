from django.contrib.admin.filters import SimpleListFilter


class SubscriptionPaymentFilter(SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = "Consistence"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "consistence"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ("consistent", "consistent"),
            ("overpaid", "overpaid"),
            ("underpaid", "underpaid"),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """

        if self.value() not in ("consistent", "overpaid", "underpaid"):
            return queryset

        subscription_payments = queryset.select_related(
            "subscription__user__profile",
            "subscription__course",
        ).prefetch_related(
            "subscription__price_reductions",
            "subscription__subscription_payments",
        )

        if self.value() == "consistent":
            ids = [
                sp.id
                for sp in subscription_payments
                if sp.subscription.sum_of_payments()
                == sp.subscription.price_after_reductions()
            ]
        elif self.value() == "overpaid":
            ids = [
                sp.id
                for sp in subscription_payments
                if sp.subscription.sum_of_payments()
                > sp.subscription.price_after_reductions()
            ]
        else:
            ids = [
                sp.id
                for sp in subscription_payments
                if sp.subscription.open_amount() > 0
            ]

        return queryset.filter(id__in=ids)
