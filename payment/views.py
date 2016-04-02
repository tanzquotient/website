from django.views.generic import TemplateView, FormView, RedirectView
from payment.forms import USIForm, VoucherForm
from courses.models import Subscribe, Voucher
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import ugettext as _

import reversion
from django.db import transaction

class VoucherPaymentIndexView(FormView):
    template_name = 'payment/voucher/form.html'
    form_class = VoucherForm

    def get_context_data(self, **kwargs):

        subscription = Subscribe.objects.filter(usi=self.kwargs['usi']).first()

        context = super(VoucherPaymentIndexView, self).get_context_data(**kwargs)
        context['subscription'] = subscription

        if subscription.payed() == True:
            self.template_name = 'payment/voucher/payment_success.html'

        return context

    def form_valid(self, form):
        self.success_url = './payed/'
        subscription = Subscribe.objects.filter(usi=self.kwargs['usi']).first()

        voucher = Voucher.objects.filter(key=form.data['voucher_code']).first()

        voucher.mark_as_used(self.request.user, comment="Used to pay course #" + subscription.usi + ".")

        if subscription.mark_as_payed('voucherpayment'):
            messages.add_message(self.request, messages.SUCCESS, _("Subscription #") + self.kwargs['usi'] + _(' successfully marked as paid.'))
        return super(VoucherPaymentIndexView, self).form_valid(form)

class VoucherPaymentSuccessView(TemplateView):

    def get_context_data(self, usi, **kwargs):
        subscription = Subscribe.objects.filter(usi=usi).first()

        if subscription.payed():
            self.template_name = 'payment/voucher/payment_success.html'
        else:
            self.template_name = 'payment/voucher/payment_failed.html'

        context = super(VoucherPaymentSuccessView, self).get_context_data(**kwargs)
        context['subscription'] = subscription

        return context

class CounterPaymentIndexView(FormView):
    template_name = 'payment/counter/form.html'
    form_class = USIForm

    def form_valid(self, form):
        self.success_url = './' + form.data['usi'] + '/details/'
        return super(CounterPaymentIndexView, self).form_valid(form)

class CounterPaymentDetailView(TemplateView):
    template_name = 'payment/counter/details.html'

    def get_context_data(self, usi, **kwargs):

        subscription = Subscribe.objects.filter(usi=usi).first()

        context = super(CounterPaymentDetailView, self).get_context_data(**kwargs)
        context['subscription'] = subscription

        return context

def counterpayment_mark_payed(request, **kwargs):
    subscription = Subscribe.objects.filter(usi=kwargs['usi']).first()

    if subscription.mark_as_payed('counterpayment', request.user):
        messages.add_message(request, messages.SUCCESS, "USI #" + kwargs['usi'] + _(' successfully marked as paid.'))
    return redirect('counterpayment_index')