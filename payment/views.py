from django.views.generic import TemplateView, FormView, RedirectView
from payment.forms import USIForm
from courses.models import Subscribe
from django.contrib import messages
from django.shortcuts import redirect

import reversion
from django.db import transaction


class IndexView(FormView):
    template_name = 'payment/form.html'
    form_class = USIForm

    def form_valid(self, form):
        self.success_url = './' + form.data['usi'] + '/details/'
        return super(CounterPaymentIndexView, self).form_valid(form)

class IndexViewfrom django.views.generic import TemplateView, FormView, RedirectView
from payment.forms import USIForm
from courses.models import Subscribe
from django.contrib import messages
from django.shortcuts import redirect

import reversion
from django.db import transaction


class VoucherPaymentIndexView(FormView):
    template_name = 'payment/form.html'
    form_class = USIForm

    def form_valid(self, form):
        self.success_url = './' + form.data['usi'] + '/details/'
        return super(CounterPaymentIndexView, self).form_valid(form)

class CounterPaymentIndexView(FormView):
    template_name = 'payment/form.html'
    form_class = USIForm

    def form_valid(self, form):
        self.success_url = './' + form.data['usi'] + '/details/'
        return super(CounterPaymentIndexView, self).form_valid(form)

class CounterPaymentDetailView(TemplateView):
    template_name = 'payment/details.html'

    def get_context_data(self, usi, **kwargs):

        subscription = Subscribe.objects.filter(usi=usi).first()

        context = super(CounterPaymentDetailView, self).get_context_data(**kwargs)
        context['subscription'] = subscription

        return context

def counterpayment_mark_payed(request, **kwargs):
    subscription = Subscribe.objects.filter(usi=kwargs['usi']).first()

    with transaction.atomic(), reversion.create_revision():
        subscription.status = 'payed'
        subscription.save()
        reversion.set_user(request.user)
        reversion.set_comment("Payed on counter")
    messages.add_message(request, messages.SUCCESS, "USI #" + kwargs['usi'] + ' successfully marked as payed')
    return redirect('counterpayment_index')(FormView):
    template_name = 'payment/form.html'
    form_class = USIForm

    def form_valid(self, form):
        self.success_url = './' + form.data['usi'] + '/details/'
        return super(CounterPaymentIndexView, self).form_valid(form)

class DetailView(TemplateView):
    template_name = 'payment/details.html'

    def get_context_data(self, usi, **kwargs):

        subscription = Subscribe.objects.filter(usi=usi).first()

        context = super(CounterPaymentDetailView, self).get_context_data(**kwargs)
        context['subscription'] = subscription

        return context

def mark_payed(request, **kwargs):
    subscription = Subscribe.objects.filter(usi=kwargs['usi']).first()

    with transaction.atomic(), reversion.create_revision():
        subscription.status = 'payed'
        subscription.save()
        reversion.set_user(request.user)
        reversion.set_comment("Payed on counter")
    messages.add_message(request, messages.SUCCESS, "USI #" + kwargs['usi'] + ' successfully marked as payed')
    return redirect('counterpayment_index')