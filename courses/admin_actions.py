from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render

from survey.models import Survey, SurveyInstance
import survey.services as survey_services
from courses.models import *
from django.contrib.auth.models import User, Group

from . import services

from django import forms

from django.utils.translation import ugettext as _
from payment.services import remind_of_payments

from django.contrib import messages


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


class CopyCourseForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    offering = forms.ModelChoiceField(queryset=Offering.objects.all(), label=_("Offering to copy into"))
    set_preceeding_course = forms.BooleanField(required=False)
    set_preceeding_course.help_text = "Should the copy of the course link to the original course as a predecessor?"


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


class RejectForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    reason = forms.ChoiceField(label=_("Select Reason"), choices=Rejection.Reason.CHOICES)
    send_email = forms.BooleanField(label=_("Inform subscriber about cancellation"), required=False)


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


def set_subscriptions_as_payed(modeladmin, request, queryset):
    queryset.filter(state=Subscribe.State.CONFIRMED).update(state=Subscribe.State.COMPLETED)


set_subscriptions_as_payed.short_description = "Set selected subscriptions as payed"


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


def export_confirmed_subscriptions_xlsx(modeladmin, request, queryset):
    ids = []
    for c in queryset:
        ids.append(c.id)
    return services.export_subscriptions(ids, 'xlsx')


export_confirmed_subscriptions_xlsx.short_description = "Export confirmed subscriptions of selected courses as XLSX"


def export_teacher_payment_information_csv(modeladmin, request, queryset):
    return services.export_teacher_payment_information(offerings=queryset.all())

export_teacher_payment_information_csv.short_description = "Export teacher payment information as CSV"


def mark_voucher_as_used(modeladmin, request, queryset):
    # mark vouchers as used
    for voucher in queryset:
        voucher.mark_as_used(user=request.user, comment="by admin action")


mark_voucher_as_used.short_description = "Mark selected vouchers as used"


class EvaluateForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    survey = forms.ModelChoiceField(label=_("Select Survey"), queryset=Survey.objects.all())
    send_invitations = forms.BooleanField(label=_("Send invitations (without reviewing)?"), initial=True,
                                          required=False)
    url_expires = forms.BooleanField(label=_("Should invitation url expire?"), initial=False, required=False)
    url_expire_date = forms.DateTimeField(label=_("URL expire date"),
                                          initial=datetime.date.today() + datetime.timedelta(days=30))


def evaluate_course(self, request, queryset):
    form = None

    if 'go' in request.POST:
        form = EvaluateForm(request.POST)

        if form.is_valid():
            survey = form.cleaned_data['survey']
            send_invitations = form.cleaned_data['send_invitations']
            url_expires = form.cleaned_data['url_expires']
            url_expire_date = form.cleaned_data['url_expire_date']

            for c in queryset:
                if c.evaluated:
                    continue
                c.evaluated = True
                c.save()
                for s in c.participatory().all():
                    inst = SurveyInstance(survey=survey, course=c, user=s.user,
                                          url_expire_date=url_expire_date if url_expires else None)
                    inst.save()
                    if send_invitations:
                        survey_services.send_invitation(inst)
            return HttpResponseRedirect(request.get_full_path())

    if not form:
        form = EvaluateForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})

    return render(request, 'courses/auth/action_evaluate.html', {'courses': queryset,
                                                                 'evaluate_form': form,
                                                                 })


evaluate_course.short_description = "Configure evaluation of selected courses"


def undo_voucher_payment(modeladmin, request, queryset):
    for subscription in queryset:
        if subscription.state in [Subscribe.State.PAYED,
                                  Subscribe.State.COMPLETED] and subscription.paymentmethod == PaymentMethod.VOUCHER:
            subscription.state = Subscribe.State.CONFIRMED
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


def update_dance_teacher_group(modeladmin=None, request=None, queryset=None):
    # ignore the queryset parameter
    teachers = Group.objects.filter(name__in=['Tanzlehrer', 'Dance Teachers', 'Teachers', 'Lehrer'])
    if teachers.count() == 0:
        if request:
            messages.add_message(request, messages.WARNING,
                             u'No suitable "Dance Teachers"-group found -> Group is automatically created')
        group = Group.objects.create(name='Dance Teachers')
    elif teachers.count() > 1:
        if request:
            messages.add_message(request, messages.ERROR,
                             u'More than one "Dance Teachers"-group found -> Nothing done')
        return
    else:
        group = teachers.first()

    group.user_set.clear()
    for teach in Teach.objects.all():
        if not group.user_set.filter(pk=teach.teacher.id).exists():
            group.user_set.add(teach.teacher)
    if request:
        messages.add_message(request, messages.SUCCESS,
                         u'{} teachers added to group {}'.format(group.user_set.count(), group.name))


class EmailListForm(forms.Form):
    pass


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
