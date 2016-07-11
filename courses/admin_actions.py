from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render

from survey.models import Survey, SurveyInstance
import survey.services as survey_services
from courses.models import *

from . import services

from django import forms

from django.utils.translation import ugettext as _


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
    for c in queryset:
        services.copy_course(c)


copy_courses.short_description = "Create copy of courses for the subsequent offering"


def confirm_subscriptions(modeladmin, request, queryset):
    # manually send confirmation mails
    services.confirm_subscriptions(queryset, request)


confirm_subscriptions.short_description = "Confirm selected subscriptions"


def confirm_subscriptions_allow_singles(modeladmin, request, queryset):
    # manually send confirmation mails
    services.confirm_subscriptions(queryset, request, True)


confirm_subscriptions_allow_singles.short_description = "Confirm selected subscriptions (allow singles in couple courses)"


class RejectForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    reason = forms.ChoiceField(label=_("Select Reason"), choices=Rejection.Reason.CHOICES)


def reject_subscriptions(self, request, queryset):
    form = None

    if 'reject' in request.POST:
        form = RejectForm(request.POST)

        if form.is_valid():
            reason = form.cleaned_data['reason']

            services.reject_subscriptions(queryset, reason)

            return HttpResponseRedirect(request.get_full_path())

    if not form:
        form = RejectForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})

    return render(request, 'courses/auth/action_reject.html', {'subscriptions': queryset,
                                                               'reason_form': form,
                                                               })


reject_subscriptions.short_description = "Reject selected subscriptions"


def match_partners(modeladmin, request, queryset):
    services.match_partners(queryset, request)


match_partners.short_description = "Match partners (chronologically, body height optimal)"


def unmatch_partners(modeladmin, request, queryset):
    services.unmatch_partners(queryset)


unmatch_partners.short_description = "Unmatch partners (both partners must be selected)"


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


def mark_voucher_as_used(modeladmin, request, queryset):
    # mark vouchers as used
    for voucher in queryset:
        voucher.used = True
        voucher.save()


mark_voucher_as_used.short_description = "Mark selected vouchers as used."


class EvaluateForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    survey = forms.ModelChoiceField(label=_("Select Survey"), queryset=Survey.objects.all())
    send_invitations = forms.BooleanField(label=_("Send invitations (without reviewing)?"), initial=True)
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
