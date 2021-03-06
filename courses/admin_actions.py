from django import forms
from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

import survey.services as survey_services
from courses.models import *
from payment.services import remind_of_payments
from survey.models import SurveyInstance
from . import services
from .admin_forms import CopyCourseForm, SendCourseEmailForm, RejectForm, EmailListForm
from .forms import VoucherGenerationForm, SendVoucherForm


def display(modeladmin, request, queryset):
    queryset.update(display=True)


display.short_description = "Set displayed"


def undisplay(modeladmin, request, queryset):
    queryset.update(display=False)


undisplay.short_description = "Set undisplayed"


def activate(modeladmin, request, queryset):
    queryset.update(active=True)


activate.short_description = "Activate"


def deactivate(modeladmin, request, queryset):
    queryset.update(active=False)


deactivate.short_description = "Deactivate"


def copy_courses(modeladmin, request, queryset):
    form = None

    if 'copy' in request.POST:
        form = CopyCourseForm(request.POST)

        if form.is_valid():
            offering = form.cleaned_data['offering']

            for c in queryset:
                services.copy_course(c, to=offering, set_preceeding_course=form.cleaned_data['set_preceeding_course'])

            return HttpResponseRedirect(request.get_full_path())

    if not form:
        form = CopyCourseForm(
            initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME),
                     'offering': services.get_subsequent_offering(),
                     'set_preceeding_course': True})

    return render(request, 'courses/auth/action_copy_course.html', {'courses': queryset,
                                                                    'copy_form': form,
                                                                    })


copy_courses.short_description = "Create copy of courses in another offering"


def confirm_subscriptions(modeladmin, request, queryset):
    # manually send confirmation mails
    services.confirm_subscriptions(queryset, request)


confirm_subscriptions.short_description = "Confirm selected subscriptions"


def confirm_subscriptions_allow_singles(modeladmin, request, queryset):
    # manually send confirmation mails
    services.confirm_subscriptions(queryset, request, True)


confirm_subscriptions_allow_singles.short_description = "Confirm selected subscriptions (allow singles in couple courses)"


def unconfirm_subscriptions(modeladmin, request, queryset):
    # manually send confirmation mails
    services.unconfirm_subscriptions(queryset, request)


unconfirm_subscriptions.short_description = "Unconfirm subscriptions (be sure to reconfirm them later!)"


def payment_reminder(modeladmin, request, queryset):
    remind_of_payments(queryset, request)

payment_reminder.short_description = "Send payment reminder to the selected subscriptions (which are in TO_PAY state)"



def reject_subscriptions(self, request, queryset):
    form = None

    if 'reject' in request.POST:
        form = RejectForm(request.POST)

        if form.is_valid():
            reason = form.cleaned_data['reason']

            services.reject_subscriptions(queryset, reason, form.cleaned_data['send_email'])

            return HttpResponseRedirect(request.get_full_path())

    if not form:
        form = RejectForm(
            initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME), 'send_email': True})

    return render(request, 'courses/auth/action_reject.html', {'subscriptions': queryset,
                                                               'reason_form': form,
                                                               })


reject_subscriptions.short_description = "Reject selected subscriptions"


def unreject_subscriptions(modeladmin, request, queryset):
    # manually send confirmation mails
    services.unreject_subscriptions(queryset, request)


unreject_subscriptions.short_description = "Unreject subscriptions"


def match_partners(modeladmin, request, queryset):
    services.match_partners(queryset, request)


match_partners.short_description = "Match partners (chronologically, body height optimal)"


def unmatch_partners(modeladmin, request, queryset):
    services.unmatch_partners(queryset, request)


unmatch_partners.short_description = "Unmatch partners (both partners must be selected and unconfirmed)"


def breakup_couple(modeladmin, request, queryset):
    services.breakup_couple(queryset, request)


breakup_couple.short_description = "Break up (unmatch) couple (both couple partners must be selected and unconfirmed)"


def correct_matching_state_to_couple(modeladmin, request, queryset):
    services.correct_matching_state_to_couple(queryset, request)


correct_matching_state_to_couple.short_description = "Correct matching_state to COUPLE (both partners must be matched together, can already be confirmed)"


def welcome_teachers(modeladmin, request, queryset):
    services.welcome_teachers(queryset, request)


def welcome_teachers_reset_flag(modeladmin, request, queryset):
    services.welcome_teachers_reset_flag(queryset, request)


def set_subscriptions_as_paid(modeladmin, request, queryset):
    queryset.filter(state=SubscribeState.CONFIRMED).update(state=SubscribeState.COMPLETED)


set_subscriptions_as_paid.short_description = "Set selected subscriptions as paid"


def export_confirmed_subscriptions_csv(modeladmin, request, queryset):
    ids = []
    for c in queryset:
        ids.append(c.id)
    return services.export_subscriptions(ids, 'csv')


export_confirmed_subscriptions_csv.short_description = "Export confirmed subscriptions of selected courses as CSV"


def export_confirmed_subscriptions_csv_google(modeladmin, request, queryset):
    ids = []
    for c in queryset:
        ids.append(c.id)
    return services.export_subscriptions(ids, 'csv_google')


export_confirmed_subscriptions_csv_google.short_description = "Export confirmed subscriptions of selected courses as Google Contacts readable CSV"


def export_confirmed_subscriptions_vcard(modeladmin, request, queryset):
    ids = []
    for c in queryset:
        ids.append(c.id)
    return services.export_subscriptions(ids, 'vcard')


export_confirmed_subscriptions_vcard.short_description = "Export confirmed subscriptions of selected courses as vCard"


def export_confirmed_subscriptions_xlsx(modeladmin, request, queryset):
    ids = []
    for c in queryset:
        ids.append(c.id)
    return services.export_subscriptions(ids, 'xlsx')


export_confirmed_subscriptions_xlsx.short_description = "Export confirmed subscriptions of selected courses as XLSX"


def export_teacher_payment_information_csv(modeladmin, request, queryset):
    return services.export_teacher_payment_information(offerings=queryset.all())

export_teacher_payment_information_csv.short_description = "Export teacher payment information as CSV"


def export_teacher_payment_information_excel(modeladmin, request, queryset):
    return services.export_teacher_payment_information(offerings=queryset.all(), export_format='excel')

export_teacher_payment_information_excel.short_description = "Export teacher payment information as Excel"


def mark_voucher_as_used(modeladmin, request, queryset):
    # mark vouchers as used
    for voucher in queryset:
        voucher.mark_as_used(user=request.user, comment="by admin action")


mark_voucher_as_used.short_description = "Mark selected vouchers as used"


def send_vouchers_for_subscriptions(modeladmin, request, queryset):
    form = None

    if 'go' in request.POST:
        form = SendVoucherForm(data=request.POST)

        if form.is_valid():
            recipients = [subscription.user for subscription in queryset]
            services.send_vouchers(data=form.cleaned_data, recipients=recipients)
            return HttpResponseRedirect(request.get_full_path())

    if not form:
        form = SendVoucherForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})

    context = {
        'form': form,
        'action': 'send_vouchers_for_subscriptions',
    }
    return render(request, 'courses/auth/action_send_voucher.html', context)

send_vouchers_for_subscriptions.short_description = "Send a voucher to users of selected subscriptions"

def send_course_email(modeladmin, request, queryset):
    form = None

    if 'go' in request.POST:
        form = SendCourseEmailForm(data=request.POST)

        if form.is_valid():
            services.send_course_email(data=form.cleaned_data, courses=queryset)
            return HttpResponseRedirect(request.get_full_path())

    if not form:
        form = SendCourseEmailForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})

    return render(request, 'courses/auth/action_send_course_email.html', {'courses': queryset,
                                                                 'evaluate_form': form,
                                                                          })


send_course_email.short_description = "Send an email to all participants of the selected course(s)"


def undo_voucher_payment(modeladmin, request, queryset):
    for subscription in queryset:
        if subscription.state in [SubscribeState.PAID,
                                  SubscribeState.COMPLETED] and subscription.paymentmethod == PaymentMethod.VOUCHER:
            subscription.state = SubscribeState.CONFIRMED
            for voucher in Voucher.objects.filter(subscription=subscription).all():
                voucher.subscription = None
                voucher.used = False
                voucher.save()
            subscription.save()


undo_voucher_payment.short_description = "Undo voucher payment"


def raise_price_to_pay(modeladmin, request, queryset):
    for subscription_payment in queryset:
        if subscription_payment.balance() > 0:
            s = subscription_payment.subscription
            s.price_to_pay = subscription_payment.amount
            s.save()


raise_price_to_pay.short_description = "raise price to pay to fit amount"


def emaillist(modeladmin, request, queryset):
    form = None

    if 'ok' in request.POST:
        form = EmailListForm(request.POST)

        if form.is_valid():
            return HttpResponseRedirect(reverse('admin:courses_subscribe_changelist'))

    if not form:
        form = EmailListForm()

    return render(request, 'courses/auth/action_emaillist.html', {
        'form': form,
        'emails': [s.user.email + ';' for s in queryset.all()],
        'message': "Email addresses of selected subscribers (note that selected filters are applied!)"
    })


emaillist.short_description = "List emails of selected subscribers"


def offering_emaillist(modeladmin, request, queryset):
    form = None

    if 'ok' in request.POST:
        form = EmailListForm(request.POST)

        if form.is_valid():
            return HttpResponseRedirect(reverse('admin:courses_offering_changelist'))

    if not form:
        form = EmailListForm()

    subscriptions = Subscribe.objects.accepted().filter(course__offering__in=queryset.all())
    return render(request, 'courses/auth/action_emaillist.html', {
        'form': form,
        'emails': [s.user.email for s in subscriptions],
        'message': "Email addresses of accepted subscribers of offerings {}".format(", ".join(map(str, queryset.all())))
    })


offering_emaillist.short_description = "List emails of accepted participants"

def make_inactive(modeladmin, request, queryset):
    for user in queryset:

        user.is_active = False
        user.save()
    messages.add_message(request, messages.SUCCESS, 'Deactivated {} profiles'.format(queryset.count()))
