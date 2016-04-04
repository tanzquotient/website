from django.views.generic import TemplateView, FormView, RedirectView
from payment.forms import USIForm, VoucherForm, CourseForm
from courses.models import Subscribe, Voucher, Course
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django import forms



class VoucherPaymentIndexView(FormView):
    template_name = 'payment/voucher/form.html'
    form_class = VoucherForm

    def get_context_data(self, **kwargs):
        context = super(VoucherPaymentIndexView, self).get_context_data(**kwargs)

        subscription = Subscribe.objects.filter(usi=self.kwargs['usi']).first()
        context['subscription'] = subscription

        # if the user has already paid, show the payment-success view
        if subscription.payed():
            self.template_name = 'payment/voucher/payment_success.html'

        return context

    def form_valid(self, form):
        # if the user entered a vaild voucher code, mark the voucher as used and redirect the user to the payment successful page

        self.success_url = reverse('payment:voucherpayment_success')

        subscription = Subscribe.objects.filter(usi=self.kwargs['usi']).first()

        voucher = Voucher.objects.filter(key=form.data['voucher_code']).first()
        voucher.mark_as_used(self.request.user, comment="Used to pay course #" + subscription.usi + ".")

        # show a message that the subscription has been payed (use django message passing framework)
        if subscription.mark_as_payed('voucherpayment'):
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Subscription #") + self.kwargs['usi'] + _(' successfully marked as paid.'))

        return super(VoucherPaymentIndexView, self).form_valid(form)


class VoucherPaymentSuccessView(TemplateView):
    def get_context_data(self, usi, **kwargs):
        subscription = Subscribe.objects.filter(usi=usi).first()

        # ensure that the payment success page is only displayed if the subscription is actually paid.
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
        self.success_url = reverse('payment:counterpayment_detail', kwargs={'usi': form.data['usi']})
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

    # redirect and show message
    if subscription.mark_as_payed('counterpayment', request.user):
        messages.add_message(request, messages.SUCCESS, "USI #" + kwargs['usi'] + _(' successfully marked as paid.'))
    return redirect('payment:counterpayment_index')


class CoursePaymentIndexView(FormView):
    template_name = 'payment/course/form.html'
    form_class = CourseForm

    def get_form_kwargs(self):
        kwargs = super(CoursePaymentIndexView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        self.success_url = reverse('payment:coursepayment_detail', kwargs={'course': form.data['course']})
        return super(CoursePaymentIndexView, self).form_valid(form)


class CoursePaymentDetailView(TemplateView):
    template_name = 'payment/course/course.html'

    def get_context_data(self, **kwargs):
        course = Course.objects.filter(id=kwargs['course']).first()

        context = super(CoursePaymentDetailView, self).get_context_data(**kwargs)
        context['course'] = course
        return context

class CoursePaymentConfirm(FormView):
    template_name = 'payment/course/confirm.html'
    form_class = forms.Form

    def get_context_data(self, **kwargs):
        subscription = Subscribe.objects.filter(usi=self.kwargs['usi']).first()

        context = super(CoursePaymentConfirm, self).get_context_data(**kwargs)
        context['subscription'] = subscription
        return context

    def form_valid(self, form):
        self.success_url = reverse('payment:coursepayment_detail', kwargs={'course' : self.kwargs['course']})
        subscription = Subscribe.objects.filter(usi=self.kwargs['usi']).first()

        # redirect and show message
        if subscription.mark_as_payed('coursepayment', self.request.user):
            messages.add_message(self.request, messages.SUCCESS, "USI #" + self.kwargs['usi'] + _(' successfully marked as paid.'))

        return super(CoursePaymentConfirm, self).form_valid(form)


