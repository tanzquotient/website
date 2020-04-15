# Register your models here.

from django.contrib.admin.views.main import ChangeList
from django.contrib.auth.admin import GroupAdmin
from parler.admin import TranslatableAdmin
from reversion.admin import VersionAdmin

from courses.filters import *
from groups.services import update_groups
from payment.vouchergenerator import generate_svg


class CourseInline(admin.TabularInline):
    model = Course
    fields = ('name', 'type', 'period', "position",)
    extra = 0


@admin.register(Offering)
class OfferingAdmin(admin.ModelAdmin):
    list_display = ('name', 'period', 'display', 'active')
    inlines = (CourseInline,)

    actions = [display, undisplay, activate, deactivate, offering_emaillist,
               export_teacher_payment_information_csv,
               export_teacher_payment_information_excel]


class TeachInlineForCourse(admin.TabularInline):
    model = Teach
    extra = 2
    fk_name = 'course'

    raw_id_fields = ('teacher',)


class TeachingLessonInline(admin.TabularInline):
    model = TeachLesson
    extra = 0
    fk_name = 'lesson'


class SubscribeInlineForCourse(admin.TabularInline):
    model = Subscribe
    extra = 1
    fk_name = 'course'

    raw_id_fields = ('user', 'partner')
    readonly_fields = ('state', 'matching_state', 'usi',)


class SubscribeInlineForUser(admin.TabularInline):
    model = Subscribe
    extra = 1
    fk_name = 'user'

    raw_id_fields = ('course', 'partner')
    readonly_fields = ('state', 'matching_state', 'usi',)


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


class PredecessorCoursesInline(admin.TabularInline):
    model = CourseSuccession
    fk_name = 'successor'
    extra = 0


class SongInline(admin.TabularInline):
    search_fields = ['title', ]
    model = Song
    extra = 5


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ['title', 'artist', 'length', 'speed', 'style']
    list_filter = ('style',)
    search_fields = ['title', 'artist', 'style__name']
    model = Song


@admin.register(LessonDetails)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['get_course', 'get_lesson', 'room',]
    inlines = (TeachingLessonInline,)


@admin.register(RegularLesson)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['course', 'weekday', 'time_from', 'time_to']
    inlines = (RegularLessonExceptionInline,)


@admin.register(Course)
class CourseAdmin(TranslatableAdmin):
    list_display = (
        'name', 'type', 'subscription_type', 'offering', 'period', 'format_lessons', 'format_cancellations',
        'room', 'format_prices',
        'format_teachers',
        'display', 'active', 'get_teachers_welcomed', 'format_preceeding_courses')
    list_filter = ('offering', 'subscription_type', 'display', 'active')
    search_fields = ['name', 'type__name', ]
    inlines = (RegularLessonInline, IrregularLessonInline, TeachInlineForCourse,
               PredecessorCoursesInline, SubscribeInlineForCourse)

    model = Course

    fieldsets = [
        ('What?', {
            'fields': ['name', 'type', 'subscription_type', 'min_subscribers', 'max_subscribers', 'description', 'external_url']}),
        ('When?', {
            'fields': ['offering', 'period']}),
        ('Where?', {
            'fields': ['room']}),
        ('Billing', {
            'fields': ['price_with_legi', 'price_without_legi', 'price_special']}),
        ('Admin', {
            'fields': ['display', 'active', 'evaluated']}),
    ]

    actions = [display, undisplay, activate, deactivate, welcome_teachers, welcome_teachers_reset_flag, copy_courses,
               export_confirmed_subscriptions_csv,
               export_confirmed_subscriptions_csv_google,
               export_confirmed_subscriptions_vcard,
               export_confirmed_subscriptions_xlsx, send_course_email]


@admin.register(CourseSuccession)
class CourseSuccession(admin.ModelAdmin):
    list_display = ['predecessor', 'successor']
    model = CourseSuccession


@admin.register(CourseType)
class CourseTypeAdmin(TranslatableAdmin):
    list_display = ('name', 'format_styles', 'level', 'couple_course',)
    list_filter = ('level', 'couple_course')
    search_fields = ['name', ]

    model = CourseType

    raw_id_fields = ('styles',)


class SubscribeChangeList(ChangeList):
    def get_results(self, *args, **kwargs):
        super(SubscribeChangeList, self).get_results(*args, **kwargs)

        self.info = {
            'total': self.result_list.count(),
            'accepted': 0,
            'rejected': 0,
            'max_subscribers': None
        }
        course_consistent = True
        course = None
        for s in self.result_list:
            if s.state in SubscribeState.ACCEPTED_STATES:
                self.info['accepted'] += 1
            if s.state == SubscribeState.REJECTED_STATES:
                self.info['rejected'] += 1
            if course_consistent:
                if course is None:
                    course = s.course
                if s.course != course:
                    course_consistent = False
        if course_consistent and course is not None:
            self.info['max_subscribers'] = course.max_subscribers


@admin.register(Subscribe)
class SubscribeAdmin(VersionAdmin):
    list_display = (
        'id', 'state', 'get_offering', 'course', 'matching_state', 'user', 'partner', 'get_user_gender',
        'get_user_body_height',
        'get_user_email', 'get_user_student_status', 'experience', 'comment', 'price_to_pay', 'get_payment_state',
        'get_calculated_experience', 'date')
    list_display_links = ('id',)
    list_filter = (SubscribeOfferingListFilter, SubscribeCourseListFilter, 'date', 'state')
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'usi']
    readonly_fields = ('state', 'usi',)

    model = Subscribe

    actions = [match_partners, unmatch_partners, breakup_couple, confirm_subscriptions, unconfirm_subscriptions,
               confirm_subscriptions_allow_singles,
               reject_subscriptions, unreject_subscriptions, correct_matching_state_to_couple,
               set_subscriptions_as_paid, undo_voucher_payment, payment_reminder, emaillist]

    raw_id_fields = ('user', 'partner')

    change_list_template = 'courses/admin/subscribe_change_list.html'

    def get_changelist(self, request):
        return SubscribeChangeList


@admin.register(Confirmation)
class ConfirmationAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'date')
    list_filter = (ConfirmationOfferingListFilter, ConfirmationCourseListFilter, 'date',)
    search_fields = ['subscription__course__name', 'subscription__course__type__name', 'subscription__user__email',
                     'subscription__user__first_name', 'subscription__user__last_name']

    model = Confirmation

    raw_id_fields = ('subscription', 'mail')


@admin.register(Rejection)
class RejectionAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'date', 'reason')
    list_filter = (ConfirmationOfferingListFilter, ConfirmationCourseListFilter, 'date',)
    search_fields = ['subscription__course__name', 'subscription__course__type__name', 'subscription__user__email',
                     'subscription__user__first_name', 'subscription__user__last_name']

    model = Rejection

    raw_id_fields = ('subscription', 'mail')


@admin.register(TeacherWelcome)
class TeacherWelcomeAdmin(admin.ModelAdmin):
    list_display = ('teach', 'date')
    search_fields = ['teach__teacher__first_name', 'teach__teacher__last_name', 'teach__course__name',
                     'teach__course__type__name']

    model = TeacherWelcome

    raw_id_fields = ('teach', 'mail')


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_from', "date_to")
    inlines = (PeriodCancellationInline,)


@admin.register(Teach)
class TeachAdmin(admin.ModelAdmin):
    raw_id_fields = ('teacher',)
    list_display = ('id', 'teacher', 'course', 'welcomed')
    list_filter = (SubscribeOfferingListFilter, SubscribeCourseListFilter,)
    list_display_link = ('id',)
    search_fields = ['teacher__email', 'teacher__first_name', 'teacher__last_name', 'course__name',
                     'course__type__name', 'hourly_wage']


@admin.register(Style)
class StyleAdmin(TranslatableAdmin):
    list_display = ('name', 'parent_style', 'filter_enabled')
    list_filter = ('filter_enabled', StyleParentFilter, StyleChildrenOfFilter)
    inlines = (SongInline,)


@admin.register(Room)
class RoomAdmin(TranslatableAdmin):
    pass


@admin.register(Voucher)
class VoucherAdmin(VersionAdmin):
    list_display = ('purpose', 'key', 'issued', 'expires', 'used', 'pdf_file')
    exclude = ('key',)

    actions = [mark_voucher_as_used, generate_svg]

    raw_id_fields = ('subscription',)


@admin.register(VoucherPurpose)
class VoucherPurposeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
