# Register your models here.
from datetime import timedelta
from decimal import Decimal
from typing import Optional

from django.contrib.admin import ModelAdmin
from django.contrib.admin.views.main import ChangeList
from django.utils import timezone
from django.utils.html import format_html_join, mark_safe
from parler.admin import TranslatableAdmin
from parler.widgets import SortedSelect
from reversion.admin import VersionAdmin
from reversion.models import Version

from courses.admin_forms.voucher_admin_form import VoucherAdminForm
from courses.filters import *
from utils import HTMLUtils, TranslationUtils
from django import forms
from django_countries.fields import CountryField

from .models import Address, Room


class RoomAdminForm(forms.ModelForm):
    address_street = forms.CharField(required=False, label="Street")
    address_plz = forms.IntegerField(required=False, label="PLZ")
    address_city = forms.CharField(required=False, label="City")
    address_country = CountryField().formfield(required=False, label="Country")

    class Meta:
        model = Room
        fields = "__all__"
        exclude = ("address_new",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        addr = None
        if self.instance and getattr(self.instance, "address", None):
            addr = self.instance.address
        # populate initial address fields if present
        if addr:
            self.fields["address_street"].initial = addr.street
            self.fields["address_plz"].initial = addr.plz
            self.fields["address_city"].initial = addr.city
            self.fields["address_country"].initial = getattr(addr, "country", None)

    def save(self, commit=True):
        instance = super().save(commit=False)

        street = self.cleaned_data.get("address_street")
        plz = self.cleaned_data.get("address_plz")
        city = self.cleaned_data.get("address_city")
        country = self.cleaned_data.get("address_country")

        if street or plz or city or country:
            # update existing address or create a new one
            addr = getattr(instance, "address", None)
            if addr is None:
                addr = Address()
            if street:
                addr.street = street
            if plz is not None:
                addr.plz = plz
            if city:
                addr.city = city
            if country:
                addr.country = country
            addr.save()
            instance.address = addr

        if commit:
            instance.save()
            self.save_m2m()

        return instance


@admin.register(Offering)
class OfferingAdmin(TranslatableAdmin):
    list_display = (
        "name",
        "period",
        "display",
        "active",
        "early_signup",
        "preview",
        "opens_soon",
        "survey",
    )

    actions = [
        display,
        undisplay,
        activate,
        deactivate,
        enable_early_signup,
        disable_early_signup,
        offering_emaillist,
        export_teacher_payment_information_csv,
        export_teacher_payment_information_excel,
    ]

    fieldsets = [
        (
            "Information",
            {
                "fields": [
                    "name",
                    "title",
                    "period",
                    "type",
                ]
            },
        ),
        (
            "Visibility",
            {
                "fields": [
                    "display",
                    "active",
                    "early_signup",
                    "early_signup_max_days",
                    "preview",
                    "opens_soon",
                    "group_into_sections",
                    "limit_courses_per_section",
                    "order",
                ]
            },
        ),
        ("Automatic survey", {"fields": ["survey"]}),
    ]


class TeachInlineForCourse(admin.TabularInline):
    model = Teach
    extra = 2
    fk_name = "course"

    raw_id_fields = ("teacher",)


class SubscribeInlineForCourse(admin.TabularInline):
    model = Subscribe
    extra = 1
    fk_name = "course"

    raw_id_fields = ("user", "partner")
    readonly_fields = (
        "state",
        "matching_state",
        "usi",
    )


class SubscribeInlineForUser(admin.TabularInline):
    model = Subscribe
    extra = 1
    fk_name = "user"

    raw_id_fields = ("course", "partner")
    readonly_fields = (
        "state",
        "matching_state",
        "usi",
    )


class IrregularLessonInline(admin.TabularInline):
    model = IrregularLesson
    extra = 0


class RegularLessonInline(admin.TabularInline):
    model = RegularLesson
    extra = 0
    show_change_link = True


class RegularLessonExceptionInline(admin.TabularInline):
    model = RegularLessonException
    extra = 0


class PeriodCancellationInline(admin.TabularInline):
    model = PeriodCancellation
    extra = 2


class RoomCancellationInline(admin.TabularInline):
    model = RoomCancellation
    extra = 2

    def get_queryset(self, request):
        return (
            super(RoomCancellationInline, self)
            .get_queryset(request)
            .filter(date__gte=timezone.now().date() - timedelta(days=90))
        )


class RoomAccessCodeInline(admin.TabularInline):
    model = RoomAccessCode
    extra = 2

    def get_queryset(self, request):
        return (
            super(RoomAccessCodeInline, self)
            .get_queryset(request)
            .filter(valid_until__gte=timezone.now().date() - timedelta(days=90))
        )


@admin.register(LessonDetails)
class MemberAdmin(admin.ModelAdmin):
    list_display = [
        "get_course",
        "get_lesson",
        "room",
    ]


@admin.register(RegularLesson)
class MemberAdmin(admin.ModelAdmin):
    list_display = ["course", "weekday", "time_from", "time_to"]
    inlines = (RegularLessonExceptionInline,)


@admin.register(Course)
class CourseAdmin(TranslatableAdmin):
    list_display = (
        "name",
        "type",
        "format_lessons_for_admin",
        "room",
        "is_displayed",
        "is_active",
        "is_early_signup_enabled",
        "is_cancelled",
        "is_evaluated",
        "are_teachers_welcomed",
        "is_partner_required_at_signup",
        "subscription_type",
        "offering",
        "get_period",
        "format_cancellations",
        "price",
        "num_lessons",
        "total_hours",
        "format_teachers",
        "has_description_in_all_languages",
    )
    list_filter = (
        "offering",
        "subscription_type",
        "display",
        "active",
        "completed",
        "partner_required_at_signup",
    )
    readonly_fields = ["completed"]
    search_fields = [
        "name",
        "type__translations__title",
    ]
    inlines = (
        RegularLessonInline,
        IrregularLessonInline,
        TeachInlineForCourse,
        SubscribeInlineForCourse,
    )
    widgets = {"type": SortedSelect}

    model = Course

    fieldsets = [
        (
            "What?",
            {
                "fields": [
                    "name",
                    "type",
                    "partner_required_at_signup",
                    "subscription_type",
                    "min_subscribers",
                    "max_subscribers",
                    "experience_mandatory",
                    "description",
                    "information_for_participants_admin",
                    "information_for_participants_teachers",
                    "external_url",
                    "partner",
                ]
            },
        ),
        ("When?", {"fields": ["offering", "period"]}),
        ("Where?", {"fields": ["room"]}),
        (
            "Billing",
            {"fields": ["price_with_legi", "price_without_legi", "price_special"]},
        ),
        (
            "Admin",
            {
                "fields": [
                    "display",
                    "active",
                    "cancelled",
                    "completed",
                    "early_signup",
                ]
            },
        ),
    ]

    actions = [
        display,
        undisplay,
        activate,
        deactivate,
        enable_early_signup,
        disable_early_signup,
        cancel,
        welcome_teachers,
        copy_courses,
        export_confirmed_subscriptions_csv,
        export_confirmed_subscriptions_csv_google,
        export_confirmed_subscriptions_vcard,
        export_confirmed_subscriptions_xlsx,
        send_course_email,
    ]

    @staticmethod
    @admin.display(description="Lessons")
    def format_lessons_for_admin(course: Course) -> str:
        return format_html_join(
            mark_safe("<br/>"),
            "{}",
            ((l,) for l in course.get_lessons_as_strings()),
        )

    @staticmethod
    @admin.display(description="E", boolean=True)
    def is_evaluated(course: Course) -> bool:
        return course.survey_instances.exists()

    @staticmethod
    @admin.display(description="C", boolean=True)
    def is_cancelled(course: Course) -> bool:
        return course.cancelled

    @staticmethod
    @admin.display(description="PR", boolean=True)
    def is_partner_required_at_signup(course: Course) -> bool:
        return course.partner_required_at_signup

    @staticmethod
    @admin.display(description="T", boolean=True)
    def are_teachers_welcomed(course: Course) -> bool:
        return course.get_teachers_welcomed()

    @staticmethod
    @admin.display(description="Price")
    def price(course: Course) -> str:
        if course.price_special:
            return course.price_special
        return f"{course.price_with_legi} / {course.price_without_legi}"

    @staticmethod
    @admin.display(description="Hours")
    def total_hours(course: Course) -> Decimal:
        return course.get_total_hours()

    @staticmethod
    @admin.display(description="#")
    def num_lessons(course: Course) -> int:
        return course.lesson_occurrences.count()

    @admin.display(boolean=True, description="Has description")
    def has_description_in_all_languages(self, obj: Course) -> bool:
        return TranslationUtils.is_field_translated_in_all_languages(
            obj, "description", HTMLUtils.html_has_text
        ) or TranslationUtils.is_field_translated_in_all_languages(
            obj.type, "description", HTMLUtils.html_has_text
        )


@admin.register(CourseType)
class CourseTypeAdmin(TranslatableAdmin):
    list_display = (
        "title",
        "format_styles",
        "level",
        "couple_course",
        "has_description_in_all_languages",
    )
    list_filter = (
        "level",
        CourseTypeStyleFilter,
        "couple_course",
    )
    search_fields = ["translations__title", "translations__subtitle"]
    filter_horizontal = ["predecessors", "styles"]

    fieldsets = [
        (
            "Information",
            {
                "fields": [
                    "title",
                    "subtitle",
                    "description",
                    "information_for_participants",
                ]
            },
        ),
        ("Details", {"fields": ["level", "styles"]}),
        ("Options", {"fields": ["couple_course", "predecessors"]}),
    ]

    model = CourseType

    @admin.display(boolean=True, description="Has description")
    def has_description_in_all_languages(self, obj: CourseType) -> bool:
        return TranslationUtils.is_field_translated_in_all_languages(
            obj, "description", HTMLUtils.html_has_text
        )


class SkillDanceLevelInline(admin.TabularInline):
    model = SkillDanceLevel
    extra = 0


@admin.register(Skill)
class SkillAdmin(ModelAdmin):
    model = Skill
    list_display = [
        "user__email",
        "user__first_name",
        "user__last_name",
        "num_known_dances",
    ]
    search_fields = ["user__first_name", "user__last_name", "user__email"]
    readonly_fields = ["user"]
    inlines = [SkillDanceLevelInline]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Skill]:
        return (
            super()
            .get_queryset(request)
            .prefetch_related("dance_levels__style", "user")
        )

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: Skill = ...) -> bool:
        return False

    @staticmethod
    @admin.display(description="Number of known dances")
    def num_known_dances(skill: Skill) -> int:
        return skill.dance_levels.count()


@admin.register(Attendance)
class AttendanceAdmin(ModelAdmin):
    model = Attendance
    list_display = [
        "id",
        "lesson_occurrence__start",
        "user_name",
        "state",
        "role",
        "lesson_occurrence__course",
    ]
    search_fields = [
        "user__first_name",
        "user__last_name",
        "user__email",
        "lesson_occurrence__course__name",
    ]
    list_filter = ["state", "role"]

    def has_add_permission(self, request, obj=None) -> bool:
        return False

    def has_change_permission(self, request, obj=...) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False

    @staticmethod
    @admin.display(description="User")
    def user_name(attendance: Attendance) -> str:
        return attendance.user.get_full_name()


class SubscribeChangeList(ChangeList):
    def get_results(self, *args, **kwargs):
        super(SubscribeChangeList, self).get_results(*args, **kwargs)

        self.info = {
            "total": self.result_list.count(),
            "accepted": 0,
            "rejected": 0,
            "max_subscribers": None,
        }
        course_consistent = True
        course = None
        for s in self.result_list:
            if s.state in SubscribeState.ACCEPTED_STATES:
                self.info["accepted"] += 1
            if s.state == SubscribeState.REJECTED_STATES:
                self.info["rejected"] += 1
            if course_consistent:
                if course is None:
                    course = s.course
                if s.course != course:
                    course_consistent = False
        if course_consistent and course is not None:
            self.info["max_subscribers"] = course.max_subscribers


@admin.register(Subscribe)
class SubscribeAdmin(VersionAdmin):
    list_display = (
        "id",
        "state",
        "get_offering",
        "course",
        "matching_state",
        "user",
        "partner",
        "lead_follow",
        "get_user_gender",
        "get_user_body_height",
        "get_user_email",
        "get_user_student_status",
        "comment",
        "experience",
        "get_calculated_experience",
        "price_to_pay",
        "open_amount",
        "get_payment_state",
        "date",
        "get_additional_info",
    )
    list_display_links = ("id",)
    list_filter = (
        SubscribeOfferingListFilter,
        "date",
        "state",
        SubscribeCourseListFilter,
    )
    search_fields = [
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
        "partner__username",
        "partner__email",
        "partner__first_name",
        "partner__last_name",
        "usi",
    ]
    readonly_fields = (
        "state",
        "usi",
    )

    model = Subscribe

    def get_queryset(self, request: HttpRequest) -> QuerySet[Subscribe]:
        return Subscribe.objects.prefetch_related(
            "partner",
            "user__profile",
            "user__subscriptions",
            "user__subscriptions__course",
            "user__subscriptions__course__offering",
            "user__subscriptions__course__type",
            "user__subscriptions__course__type__translations",
            "user__subscriptions__course__type__styles",
            "price_reductions",
            "subscription_payments",
            "course",
            "course__period",
            "course__offering",
            "course__offering__period",
            "course__type",
            "course__type__styles",
            "course__type__styles__parent_style",
        )

    actions = [
        match_partners,
        unmatch_partners,
        breakup_couple,
        confirm_subscriptions,
        unconfirm_subscriptions,
        confirm_subscriptions_allow_singles,
        reject_subscriptions,
        unreject_subscriptions,
        correct_matching_state_to_couple,
        emaillist,
        send_vouchers_for_subscriptions,
        admit_from_waiting_list,
        move_to_waiting_list,
    ]

    raw_id_fields = ("user", "partner", "course")

    change_list_template = "courses/admin/subscribe_change_list.html"

    def get_changelist(self, request):
        return SubscribeChangeList

    @staticmethod
    @admin.action(description="Calculated experience")
    def get_calculated_experience(subscription: Subscribe) -> str:
        from courses.services import calculate_relevant_experience

        def format_experience_item(item: tuple[CourseType, int]) -> str:
            type, count = item
            return str(type) + (f" ({count}x)" if count > 1 else "")

        relevant_courses = list(calculate_relevant_experience(subscription))
        limit = 3
        result = ", ".join(map(format_experience_item, relevant_courses[:limit]))

        if len(relevant_courses) > limit:
            result += f", plus {len(relevant_courses) - limit} more"

        return result

    @staticmethod
    @admin.action(description="Paid?")
    def get_payment_state(subscription: Subscribe) -> str:
        """searches for courses that the user did before in the system"""
        c = len(
            [
                other_subscription
                for other_subscription in subscription.user.subscriptions.all()
                if other_subscription.course != subscription.course
                and other_subscription.state in SubscribeState.TO_PAY_STATES
            ]
        )
        if subscription.paid():
            r = "Yes"
        else:
            r = "No"

        if c > 0:
            # this user didn't pay for other courses
            r += ", owes {} more".format(c)
        return r

    @staticmethod
    @admin.action(description="Additional Info")
    def get_additional_info(subscription: Subscribe) -> Optional[str]:
        if subscription.rejections.exists():
            reason = ", ".join([r.reason for r in subscription.rejections.all()])
            return f"Rejected: {reason}"

        return None


@admin.register(Confirmation)
class ConfirmationAdmin(admin.ModelAdmin):
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

    model = Confirmation

    raw_id_fields = ("subscription", "mail")


@admin.register(Rejection)
class RejectionAdmin(admin.ModelAdmin):
    list_display = ("subscription", "date", "reason")
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

    model = Rejection

    raw_id_fields = ("subscription", "mail")


@admin.register(TeacherWelcome)
class TeacherWelcomeAdmin(admin.ModelAdmin):
    list_display = ("teach", "date")
    search_fields = [
        "teach__teacher__first_name",
        "teach__teacher__last_name",
        "teach__course__name",
        "teach__course__type__translations__title",
    ]

    model = TeacherWelcome

    raw_id_fields = ("teach", "mail")


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ("name", "date_from", "date_to")
    inlines = (PeriodCancellationInline,)


@admin.register(Teach)
class TeachAdmin(admin.ModelAdmin):
    raw_id_fields = ("teacher",)
    list_display = ("id", "teacher", "course", "welcomed")
    list_filter = (
        SubscribeOfferingListFilter,
        SubscribeCourseListFilter,
    )
    list_display_link = ("id",)
    search_fields = [
        "teacher__email",
        "teacher__first_name",
        "teacher__last_name",
        "course__name",
        "course__type__translations__title",
    ]


@admin.register(Style)
class StyleAdmin(TranslatableAdmin):
    list_display = ("name", "parent_style", "filter_enabled")
    list_filter = ("filter_enabled", StyleParentFilter, StyleChildrenOfFilter)


@admin.register(Room)
class RoomAdmin(TranslatableAdmin):
    fieldsets = [
        (
            "Information",
            {
                "fields": [
                    "name",
                    "address_street",
                    "address_plz",
                    "address_city",
                    "address_country",
                    "url",
                    "contact_info",
                ]
            },
        )
    ]
    form = RoomAdminForm
    search_fields = ["name"]
    inlines = (RoomCancellationInline, RoomAccessCodeInline)


@admin.register(RoomCancellation)
class RoomCancellationAdmin(admin.ModelAdmin):
    list_display = ["__str__", "date", "room"]
    search_fields = ["name", "room"]
    list_filter = ["date", RoomCancellationFilter]


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    pass


@admin.register(Voucher)
class VoucherAdmin(VersionAdmin):
    form = VoucherAdminForm
    list_display = (
        "key",
        "purpose",
        "comment_shortened",
        "percentage",
        "amount",
        "redeemed_amount",
        "issued",
        "issuer",
        "sent_to_full_name",
        "redeemer",
        "used_timestamp",
        "offering",
        "course",
        "pdf_file",
        "expires",
    )
    list_filter = (
        "used",
        VoucherSentFilter,
        "purpose",
        VoucherOfferingListFilter,
        VoucherCourseListFilter,
        VoucherYearUsedListFilter,
    )
    search_fields = [
        "key",
        "subscription__user__first_name",
        "subscription__user__last_name",
        "subscription__user__username",
        "subscription__user__email",
        "sent_to__first_name",
        "sent_to__last_name",
        "sent_to__username",
        "sent_to__email",
    ]
    actions = [
        mark_voucher_as_used,
        export_vouchers_csv,
        export_vouchers_xlsx,
        email_vouchers,
        download_vouchers,
    ]
    readonly_fields = ("key", "used", "pdf_file", "subscription")
    raw_id_fields = ["sent_to"]

    def sent_to_full_name(self, voucher: Voucher) -> Optional[str]:
        if voucher.sent_to:
            return voucher.sent_to.get_full_name()

    sent_to_full_name.short_description = "sent to"

    def comment_shortened(self, voucher: Voucher, max_len: int = 30) -> Optional[str]:
        if voucher.comment and len(voucher.comment) > max_len:
            return voucher.comment[:max_len] + "[...]"
        else:
            return voucher.comment

    comment_shortened.short_description = "comment"

    @staticmethod
    def percentage(voucher: Voucher) -> Optional[str]:
        if voucher.percentage:
            return voucher.percentage

    @staticmethod
    def amount(voucher: Voucher) -> Optional[str]:
        if voucher.amount:
            return voucher.amount

    @staticmethod
    def redeemed_amount(voucher: Voucher) -> Optional[str]:
        tot_amount = sum(
            [reduction.amount for reduction in voucher.price_reductions.all()]
        )
        if tot_amount != 0:
            return tot_amount

    @staticmethod
    def issuer(voucher: Voucher) -> Optional[str]:
        first_version = (
            Version.objects.get_for_object(voucher)
            .order_by("revision__date_created")
            .first()
        )

        if not first_version:
            return None

        issuer = first_version.revision.user

        if issuer:
            return issuer.get_full_name()

    @staticmethod
    def used_timestamp(voucher: Voucher) -> Optional[str]:
        if voucher.price_reductions.exists():
            return voucher.price_reductions.first().created_at

    @staticmethod
    def offering(voucher: Voucher) -> Optional[str]:
        if voucher.subscription:
            return voucher.subscription.course.offering.name

    @staticmethod
    def course(voucher: Voucher) -> Optional[str]:
        if voucher.subscription:
            return voucher.subscription.course.type.title

    @staticmethod
    def redeemer(voucher: Voucher) -> Optional[str]:
        if voucher.subscription:
            return voucher.subscription.user.get_full_name()


@admin.register(VoucherPurpose)
class VoucherPurposeAdmin(admin.ModelAdmin):
    list_display = ("name", "description")


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    search_fields = [
        "iban",
        "user_profile__user__first_name",
        "user_profile__user__last_name",
    ]
    list_display = ["user", "iban", "bank_name"]

    def get_queryset(self, request: HttpRequest) -> QuerySet[BankAccount]:
        return BankAccount.objects.prefetch_related("user_profile__user")

    @staticmethod
    def user(account: BankAccount) -> str:
        return account.user_profile.user.get_full_name()


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    readonly_fields = ["address", "bank_account"]
