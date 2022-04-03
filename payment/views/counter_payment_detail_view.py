from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.generic import FormView

from courses.models import Subscribe, PaymentMethod


class CounterPaymentDetailView(FormView):
    form_class = forms.Form
    template_name = 'payment/counter/details.html'
    success_url = reverse_lazy('payment:counterpayment_index')

    def get_context_data(self, **kwargs):
        usi = self.kwargs['usi']
        subscription = Subscribe.objects.filter(usi=usi).first()

        context = super(CounterPaymentDetailView, self).get_context_data(**kwargs)
        context['subscription'] = subscription

        return context

    @method_decorator(permission_required('courses.access_counterpayment'))
    def dispatch(self, *args, **kwargs):
        return super(CounterPaymentDetailView, self).dispatch(*args, **kwargs)

    def form_valid(self, form, **kwargs):
        usi = self.kwargs['usi']
        subscription = Subscribe.objects.filter(usi=usi).first()

        # redirect and show message
        if subscription.mark_as_paid(PaymentMethod.COUNTER, self.request.user):
            messages.add_message(self.request, messages.SUCCESS,
                                 "USI " + usi + " " + _('successfully marked as paid.'))

        return super(CounterPaymentDetailView, self).form_valid(form)