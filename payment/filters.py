from django.contrib.admin.filters import SimpleListFilter


class SubscriptionPaymentFilter(SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Consistence'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'consistence'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (('consistent', 'consistent'), ('overpaid', 'overpaid'), ('underpaid', 'underpaid'))

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """

        if self.value() == 'consistent':
            return queryset.filter(id__in=[
                sp.id for sp in queryset.all()
                if sp.subscription.sum_of_payments() == sp.subscription.price_after_reductions()])
        elif self.value() == 'overpaid':
            return queryset.filter(id__in=[
                sp.id for sp in queryset.all()
                if sp.subscription.sum_of_payments() > sp.subscription.price_after_reductions()])
        elif self.value() == 'underpaid':
            return queryset.filter(id__in=[sp.id for sp in queryset.all() if sp.subscription.open_amount() > 0])
        else:
            return queryset
