from django import forms
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView
from django.views.generic.edit import ProcessFormView, FormMixin

from courses.models import Offering, Subscribe, SubscribeState
from payment.services import remind_of_payment


class OfferingFinanceUnpaidView(PermissionRequiredMixin, TemplateView, ProcessFormView, FormMixin):
    template_name = 'finance/offering/unpaid/index.html'
    permission_required = 'payment.payment.change'
    form_class = forms.Form

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        context['active'] = "unpaid"
        context['offering'] = get_object_or_404(Offering, id=kwargs['offering'])
        context['subscriptions'] = Subscribe.objects.filter(course__offering_id=kwargs['offering'],
                                                            state=SubscribeState.CONFIRMED).select_related(
            'user', 'user__profile', 'course', 'course__offering').prefetch_related('payment_reminders').all()
        return context

    def post(self, request, **kwargs):
        self.success_url = reverse('payment:offering_finance_detail_view', kwargs=kwargs)

        subscription = Subscribe.objects.get(id=request.POST['subscription'])
        remind_of_payment(subscription)

        return super(OfferingFinanceUnpaidView, self).post(request)