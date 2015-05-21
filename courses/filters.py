from django.contrib import admin

# Register your models here.
from courses.models import *

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from courses.admin_actions import *
from django.contrib.admin.filters import SimpleListFilter


class SubscribeOfferingListFilter(SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Offering'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'offering'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """

        filters = ()
        for o in Offering.objects.all():
            filters += ((o.id, o.name),)

        return filters

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """

        if self.value() is not None:
            return queryset.filter(course__offering__id=self.value())
        else:
            return queryset
