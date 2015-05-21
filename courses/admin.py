#!/usr/bin/python
# -*- coding: UTF-8 -*-

from django.contrib import admin

# Register your models here.
from courses.models import *

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from courses.admin_actions import *
from django.contrib.admin.filters import SimpleListFilter
from courses.filters import SubscribeOfferingListFilter


class CourseInline(admin.TabularInline):
    model = Course
    fields = ('name', 'type', 'period', "position",)
    extra = 0


class OfferingAdmin(admin.ModelAdmin):
    list_display = ('name', 'period', 'display', 'active')
    inlines = (CourseInline,)


class TeachInlineForCourse(admin.TabularInline):
    model = Teach
    extra = 2
    fk_name = 'course'

    raw_id_fields = ('teacher',)


class SubscribeInlineForCourse(admin.TabularInline):
    model = Subscribe
    extra = 1
    fk_name = 'course'

    raw_id_fields = ('user', 'partner')


class SubscribeInlineForUser(admin.TabularInline):
    model = Subscribe
    extra = 1
    fk_name = 'user'

    raw_id_fields = ('course', 'partner')


class CourseCancellationInline(admin.TabularInline):
    model = CourseCancellation
    extra = 1


class CourseTimeInline(admin.TabularInline):
    model = CourseTime
    extra = 0


class PeriodCancellationInline(admin.TabularInline):
    model = PeriodCancellation
    extra = 2


class SongInline(admin.TabularInline):
    search_fields = ['title', ]
    model = Song
    extra = 5


class SongAdmin(admin.ModelAdmin):
    list_display = ['title', 'artist', 'length', 'speed', 'style']
    search_fields = ['title', 'artist', 'style__name']
    model = Song


class CourseAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'type', 'open_class', 'offering', 'period', 'format_times', 'room', 'format_prices', 'format_teachers',
        'active')
    list_filter = ('offering', 'type', 'room', 'active')
    search_fields = ['name', 'type__name', ]
    inlines = (CourseCancellationInline, CourseTimeInline, TeachInlineForCourse, SubscribeInlineForCourse,)

    model = Course
    fieldsets = [
        ('What?', {
            'fields': ['name', 'type', 'open_class', 'min_subscribers', 'max_subscribers', 'special']}),
        ('When?', {
            'fields': ['offering', 'period', ]}),
        ('Where?', {
            'fields': ['room']}),
        ('Billing', {
            'fields': ['price_with_legi', 'price_without_legi', 'price_special']}),
        ('Admin', {
            'fields': ['active']}),
    ]

    actions = [activate_courses, deactivate_courses, copy_courses, export_confirmed_subscriptions_csv,
               export_confirmed_subscriptions_xlsx, ]


class CourseTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'format_styles', 'level', 'couple_course',)
    list_filter = ('level', 'couple_course')
    search_fields = ['name', ]

    model = CourseType

    raw_id_fields = ('styles',)


class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'confirmed', 'get_offering', 'course', 'user', 'partner', 'get_user_gender', 'get_user_body_height',
        'get_user_email', 'experience', 'comment', 'get_payment_status', 'get_calculated_experience', 'date')
    list_display_links = ('id',)
    list_filter = (SubscribeOfferingListFilter, 'course', 'date', 'payed', 'confirmed')
    search_fields = ['user__email', 'user__first_name', 'user__last_name']

    model = Subscribe

    actions = [match_partners, confirm_subscriptions, set_subscriptions_as_payed]

    raw_id_fields = ('user', 'partner')


class ConfirmationAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'date')
    list_filter = ('subscription__course', 'date',)
    search_fields = ['subscription__course__name', 'subscription__course__type__name', 'subscription__user__email',
                     'subscription__user__first_name', 'subscription__user__last_name']

    model = Confirmation

    raw_id_fields = ('subscription',)


class PeriodAdmin(admin.ModelAdmin):
    inlines = (PeriodCancellationInline,)


class TeachAdmin(admin.ModelAdmin):
    raw_id_fields = ('teacher',)
    list_display = ('id', 'teacher', 'course',)
    list_display_link = ('id',)
    search_fields = ['teacher__email', 'teacher__first_name', 'teacher__last_name', 'course__name',
                     'course__type__name']


class StyleAdmin(admin.ModelAdmin):
    list_display = ('name', 'url_info', 'url_video',)
    inlines = (SongInline,)


admin.site.register(Offering, OfferingAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(CourseType, CourseTypeAdmin)
admin.site.register(Room)
admin.site.register(Song, SongAdmin)
admin.site.register(Address)
admin.site.register(Period, PeriodAdmin)
admin.site.register(Style, StyleAdmin)
admin.site.register(Teach, TeachAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
admin.site.register(Confirmation, ConfirmationAdmin)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False


# Define a new User admin
class MyUserAdmin(UserAdmin):
    inlines = (UserProfileInline, SubscribeInlineForUser)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)
