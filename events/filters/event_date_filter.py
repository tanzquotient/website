from datetime import date, datetime

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class EventDateFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Date')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'date'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('upcoming', _('Upcoming')),
            ('this_year', _('This year')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() == 'upcoming':
            return queryset.filter(date__gte=datetime.today())
        if self.value() == 'upcoming':
            return queryset.filter(date__gte=date(year=datetime.today().year, day=1, month=1))
