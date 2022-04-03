from django import forms
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import TemplateView
from django.views.generic.edit import ProcessFormView, FormMixin

from courses.models import Offering, Subscribe, SubscribeState
from payment.services import remind_of_payment


class OfferingFinanceDetailView(PermissionRequiredMixin, TemplateView, ProcessFormView, FormMixin):
    template_name = 'payment/finance/offering_detail.html'
    permission_required = 'payment.payment.change'
    form_class = forms.Form

    def get_context_data(self, **kwargs):
        context = super(OfferingFinanceDetailView, self).get_context_data(**kwargs)
        if 'offering' in kwargs.keys():
            offering = Offering.objects.get(id=kwargs['offering'])
        else:
            offering = Offering.objects.filter(active=True).first()
        context['offering'] = offering
        context['subscriptions'] = Subscribe.objects.filter(course__offering=offering,
                                                            state=SubscribeState.CONFIRMED).select_related(
            'user', 'user__profile', 'course', 'course__offering').prefetch_related('payment_reminders').all()
        return context

    def post(self, request, **kwargs):
        self.success_url = reverse('payment:offering_finance_detail_view', kwargs=kwargs)

        subscription = Subscribe.objects.get(id=request.POST['subscription'])
        remind_of_payment(subscription)

        return super(OfferingFinanceDetailView, self).post(request)