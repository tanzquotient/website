from django.contrib.admin.filters import SimpleListFilter
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from courses.admin_actions import *


class SubscribeOfferingListFilter(SimpleListFilter):
    title = "Offering"
    parameter_name = "offering"

    def lookups(self, request, model_admin):
        return [(o.id, o.name) for o in Offering.objects.all()[:15]]

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset

        return queryset.filter(course__offering__id=self.value())


class SubscribeCourseListFilter(SimpleListFilter):
    title = "Course"

    parameter_name = "course"

    def lookups(self, request: HttpRequest, model_admin) -> list[tuple[int, str]]:
        offering_id = (request.GET or dict()).get("offering")
        if not offering_id:
            return []

        return [
            (c.id, c.name) for c in Course.objects.filter(offering=offering_id).all()
        ]

    def queryset(
        self, request: HttpRequest, queryset: QuerySet[Subscribe]
    ) -> QuerySet[Subscribe]:
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


class VoucherCourseListFilter(SimpleListFilter):
    title = "Course"
    parameter_name = "course"

    def lookups(self, request, model_admin):
        if "offering" in (request.GET or set()):
            return [
                (c.id, c.name)
                for c in Course.objects.filter(offering=request.GET["offering"]).all()
            ]

        return []

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(subscription__course=self.value())

        return queryset


class VoucherOfferingListFilter(SimpleListFilter):
    title = "Offering"
    parameter_name = "offering"

    def lookups(self, request, model_admin):
        return [(o.id, o.name) for o in Offering.objects.all()[:15]]

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(subscription__course__offering=self.value())
        return queryset


class VoucherYearUsedListFilter(SimpleListFilter):
    title = "Year"
    parameter_name = "year_used"

    def lookups(self, request, model_admin):
        years = [
            reduction.created_at.year
            for reduction in PriceReduction.objects.filter(
                used_voucher__isnull=False
            ).all()
        ]
        return [(year, year) for year in set(years)]

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(price_reductions__created_at__year=self.value())
        return queryset
    

class VoucherSentFilter(admin.SimpleListFilter):
    title = _("Sent")
    parameter_name = "sent"

    def lookups(self, request, model_admin):
        return [
            ("1", _("Yes")),
            ("0", _("No")),
        ]

    def queryset(self, request, queryset):
        if self.value() == "1":
            return queryset.exclude(
                sent_to=None
            )
        if self.value() == "0":
            return queryset.filter(
                sent_to=None
            )



# Class to filter vouchers by issuer -- not working yet
# class VoucherIssuerListFilter(SimpleListFilter):
#     title = "Issuer"
#     parameter_name = "issuer"

#     def lookups(self, request, model_admin):
#         users = {version.revision.user for version in Version.objects.get_for_model(Voucher).all() if version.revision.user}

#         return [(user.id, user.get_full_name()) for user in sorted(users, key=lambda u: u.get_full_name())]

#     def queryset(self, request, queryset):
#         if self.value() is not None:
#             return [voucher for voucher in queryset.all() if Version.objects.get_for_object(voucher).order_by("revision__date_created").first().revision.user == self.value()]
#         return queryset


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
