from django.contrib.admin.filters import SimpleListFilter
from django.utils.translation import gettext_lazy as _

from courses.admin_actions import *


class SubscribeOfferingListFilter(SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = "Offering"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "offering"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        filters = ()

        current = services.get_current_active_offering()
        if current is not None:
            filters += (("current", "Current ({})".format(current.name)),)

        for o in Offering.objects.all():
            filters += ((o.id, o.name),)

        return filters

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        current = services.get_current_active_offering()

        if self.value() is None:
            return queryset
        elif self.value() == "current":
            return self.filter_by_offering(queryset, current.id)
        else:
            return self.filter_by_offering(queryset, self.value())

    @staticmethod
    def filter_by_offering(queryset, offering_id):
        """
        This is a helper method that can be overridden in subclasses to make
        this filter usable for other models.
        :param queryset: the queryset to be filtered
        :param offering_id: the id of the offering to keep in queryset
        :return the filtered queryset
        """
        return queryset.filter(course__offering__id=offering_id)


class SubscribeCourseListFilter(SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = "Course"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "course"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """

        current = services.get_current_active_offering()

        filters = ()
        o = None
        if request.GET is not None and "offering" in request.GET:
            o = request.GET["offering"]
            if o == "current":
                o = current.id
        for c in Course.objects.filter(offering=o).all():
            filters += ((c.id, c.name),)

        return filters

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """

        if self.value() is not None:
            return self.filter_by_course(queryset, self.value())
        else:
            return queryset

    @staticmethod
    def filter_by_course(queryset, course_id):
        """
        This is a helper method that can be overridden in subclasses to make
        this filter usable for other models.
        :param queryset: the queryset to be filtered
        :param offering_id: the id of the offering to keep in queryset
        :return the filtered queryset
        """
        return queryset.filter(course__id=course_id)


class ConfirmationOfferingListFilter(SubscribeOfferingListFilter):
    @staticmethod
    def filter_by_offering(queryset, offering_id):
        return queryset.filter(subscription__course__offering__id=offering_id)


class ConfirmationCourseListFilter(SubscribeCourseListFilter):
    @staticmethod
    def filter_by_course(queryset, course_id):
        return queryset.filter(subscription__course__id=course_id)


class CourseTypeStyleFilter(SimpleListFilter):
    title = _("Style")

    parameter_name = "parent"

    def lookups(self, request, model_admin):
        return [(s.name, s.name) for s in Style.objects.all() if s.children.exists()]

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            style = Style.objects.get(name=self.value())
            children = [
                s.id for s in Style.objects.all() if s == style or s.is_child_of(style)
            ]
            return queryset.filter(styles__in=children).distinct()


class StyleParentFilter(SimpleListFilter):
    title = "parent style"

    parameter_name = "parent"

    def lookups(self, request, model_admin):
        return [(s.name, s.name) for s in Style.objects.all() if s.children.exists()]

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            return queryset.filter(parent_style__name=self.value())


class StyleChildrenOfFilter(SimpleListFilter):
    title = "children of"

    parameter_name = "children_of"

    def lookups(self, request, model_admin):
        return [(s.name, s.name) for s in Style.objects.all() if s.children.exists()]

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            style = Style.objects.get(name=self.value())
            children = [s.name for s in queryset if s.is_child_of(style)]
            return queryset.filter(name__in=children)
