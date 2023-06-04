import datetime
import logging

from django import forms
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Sum
from django.urls import reverse
from django.views.generic import TemplateView
from django.views.generic.edit import ProcessFormView, FormMixin

from payment.models import Payment
from payment.models.choices import Type, CreditDebit

log = logging.getLogger("tq")


class AccountFinanceDetailView(
    PermissionRequiredMixin, TemplateView, ProcessFormView, FormMixin
):
    template_name = "finance/account/detail.html"
    permission_required = "payment.change_payment"
    form_class = forms.Form

    def _filter(self):
        def to_int(s):
            if s is None:
                return None
            try:
                return int(s)
            except ValueError as e:
                return None

        year = to_int(self.request.GET.get("year"))
        month = to_int(self.request.GET.get("month"))
        filter = self.request.GET.get("filter")
        payments = Payment.objects
        if year:
            payments = payments.filter(date__year=year)
        if month:
            payments = payments.filter(date__month=month)
        if filter and filter == "true":
            filter = True
            payments = payments.exclude(
                type__in=[
                    Type.SUBSCRIPTION_PAYMENT,
                    Type.SUBSCRIPTION_PAYMENT_TO_REIMBURSE,
                ]
            )
        else:
            filter = False
        return year, month, filter, payments

    def get_context_data(self, **kwargs):
        context = super(AccountFinanceDetailView, self).get_context_data(**kwargs)

        year, month, filter, payments = self._filter()

        context["filter"] = filter
        context["year"] = year
        context["month"] = month
        context["month_name"] = (
            datetime.date(year=2000, month=int(month), day=1).strftime("%B")
            if month
            else None
        )
        payments = payments.all()
        context["payments"] = payments
        context["total_credit"] = (
            "%.2f"
            % sum([p.amount for p in payments if p.credit_debit == CreditDebit.CREDIT])
        ).replace(
            ".", ","
        )  # replace function after float formatting to have decimal separator for German numbering format
        context["total_debit"] = (
            "%.2f"
            % sum([p.amount for p in payments if p.credit_debit == CreditDebit.DEBIT])
        ).replace(".", ",")
        context["total_unknown"] = (
            "%.2f"
            % sum([p.amount for p in payments if p.credit_debit == CreditDebit.UNKNOWN])
        ).replace(".", ",")

        # Summary
        total_subscription_payment = (
            payments.filter(
                type__in=[
                    Type.SUBSCRIPTION_PAYMENT,
                    Type.SUBSCRIPTION_PAYMENT_TO_REIMBURSE,
                ],
                credit_debit=CreditDebit.CREDIT,
            )
            .all()
            .aggregate(Sum("amount"))["amount__sum"]
            or 0
        )
        total_course_payment_transfer = (
            payments.filter(
                type__in=[Type.COURSE_PAYMENT_TRANSFER], credit_debit=CreditDebit.CREDIT
            )
            .all()
            .aggregate(Sum("amount"))["amount__sum"]
            or 0
        )
        summary = {
            "TOTAL subscription_payment": "{} CHF".format(total_subscription_payment),
            "TOTAL course_payment_transfer": "{} CHF".format(
                total_course_payment_transfer
            ),
            "TOTAL subscription_payment + course_payment_transfer": "{} CHF".format(
                total_subscription_payment + total_course_payment_transfer
            ),
        }
        context["summary"] = summary

        return context

    def post(self, request, **kwargs):
        log.debug(self.success_url)
        year, month, filter, payments = self._filter()

        self.success_url = "{}?year={}&month={}&filter={}".format(
            reverse("payment:account_finance_detail_view", kwargs=kwargs),
            year,
            month,
            filter,
        )

        for p in payments:
            p.comment = self.request.POST["comment-{}".format(p.id)]
            p.save()

        return super(AccountFinanceDetailView, self).post(request)
