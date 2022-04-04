from django import forms
from django.contrib import messages
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.generic import FormView

from courses.models import Subscribe, PaymentMethod
from . import TeacherOfCourseOnly


class CoursePaymentConfirm(FormView, TeacherOfCourseOnly):
    template_name = 'payment/courses/confirm.html'
    form_class = forms.Form

    def get_context_data(self, **kwargs):
        subscription = Subscribe.objects.filter(usi=self.kwargs['usi']).first()

        context = super(CoursePaymentConfirm, self).get_context_data(**kwargs)
        context['subscription'] = subscription
        return context

    def form_valid(self, form):
        self.success_url = reverse('payment:coursepayment_detail', kwargs={'course': self.kwargs['course']})
        subscription = Subscribe.objects.filter(usi=self.kwargs['usi']).first()

        # redirect and show message
        if subscription.mark_as_paid(PaymentMethod.COURSE, self.request.user):
            messages.add_message(self.request, messages.SUCCESS,
                                 "USI " + self.kwargs['usi'] + _(' successfully marked as paid.'))

        return super(CoursePaymentConfirm, self).form_valid(form)