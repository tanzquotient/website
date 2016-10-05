from django.http import Http404
from django.views.generic import TemplateView, FormView, RedirectView, View
from payment.forms import USIForm, VoucherForm, CourseForm
from courses.models import Subscribe, Voucher, Course, PaymentMethod, Offering
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse, reverse_lazy
from django import forms
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required, login_required
from django.core.exceptions import PermissionDenied


class VoucherPaymentIndexView(FormView):
    template_name = 'payment/voucher/form.html'
    form_class = VoucherForm

    def get_context_data(self, **kwargs):
        context = super(VoucherPaymentIndexView, self).get_context_data(**kwargs)

        subscription = Subscribe.objects.filter(usi=self.kwargs['usi']).first()
        if not subscription:
            raise Http404("Subscription with this USI does not exist")
        context['subscription'] = subscription

        # if the user has already paid, show the payment-success view
        if subscription.payed():
            self.template_name = 'payment/voucher/payment_success.html'

        return context

    def form_valid(self, form):
        # if the user entered a vaild voucher code, mark the voucher as used and redirect the user to the payment successful page

        self.success_url = reverse('payment:voucherpayment_success', kwargs={'usi': self.kwargs['usi']})

        subscription = Subscribe.objects.filter(usi=self.kwargs['usi']).first()

        voucher = Voucher.objects.filter(key=form.data['voucher_code']).first()
        voucher.mark_as_used(self.request.user, comment="Used to pay course #" + subscription.usi + ".")

        # show a message that the subscription has been payed (use django message passing framework)
        if subscription.mark_as_payed('voucher'):
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
        self.success_url = reverse('payment:counterpayment_detail', kwargs={'usi': form.data['usi'].strip('#')})
        return super(CounterPaymentIndexView, self).form_valid(form)

    @method_decorator(permission_required('courses.access_counterpayment'))
    def dispatch(self, *args, **kwargs):
        return super(CounterPaymentIndexView, self).dispatch(*args, **kwargs)


class CounterPaymentDetailView(FormView):
    form_class = forms.Form
    template_name = 'payment/counter/details.html'
    success_url = reverse_lazy('payment:counterpayment_index')

    def get_context_data(self,  **kwargs):
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
        if subscription.mark_as_payed(PaymentMethod.COUNTER, self.request.user):
            messages.add_message(self.request, messages.SUCCESS,
                                 "USI #" + usi + " " + _('successfully marked as paid.'))

        return super(CounterPaymentDetailView, self).form_valid(form)



class TeacherOnly(View):
    """
    Mixin to ensure only teachers can access a view.
    """

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        # check permissions not expressed by auth.perm
        if not self.request.user.is_staff and not self.request.user.profile.is_teacher():
            raise PermissionDenied

        return super(TeacherOnly, self).dispatch(*args, **kwargs)


class TeacherOfCourseOnly(View):
    """
    Mixin to ensure only teachers of a specific course can access a course specific view.
    The specific view is defined by course parameter in kwargs!
    """

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        # check permissions not expressed by auth.perm
        if not self.request.user.is_staff and not self.request.user.teaching.filter(
                course__id=kwargs['course']).count():
            raise PermissionDenied

        return super(TeacherOfCourseOnly, self).dispatch(*args, **kwargs)


class CoursePaymentIndexView(FormView, TeacherOnly):
    template_name = 'payment/course/form.html'
    form_class = CourseForm

    def get_form_kwargs(self):
        kwargs = super(CoursePaymentIndexView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        self.success_url = reverse('payment:coursepayment_detail', kwargs={'course': form.data['course']})
        return super(CoursePaymentIndexView, self).form_valid(form)


class CoursePaymentDetailView(TemplateView, TeacherOfCourseOnly):
    template_name = 'payment/course/course.html'

    def get_context_data(self, **kwargs):
        course = Course.objects.filter(id=kwargs['course']).first()

        context = super(CoursePaymentDetailView, self).get_context_data(**kwargs)
        context['course'] = course
        return context


class CoursePaymentConfirm(FormView, TeacherOfCourseOnly):
    template_name = 'payment/course/confirm.html'
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
        if subscription.mark_as_payed('course', self.request.user):
            messages.add_message(self.request, messages.SUCCESS,
                                 "USI #" + self.kwargs['usi'] + _(' successfully marked as paid.'))

        return super(CoursePaymentConfirm, self).form_valid(form)


class CoursePaymentExport(TeacherOfCourseOnly):
    def get(self, request, *args, **kwargs):
        from courses import services
        return services.export_subscriptions([kwargs.get('course_id', None)], 'xlsx')

class QuarterPaymentDetailView(TemplateView):
    template_name = 'payment/finance/detail.html'

    def get_context_data(self, **kwargs):
        context = super(QuarterPaymentDetailView, self).get_context_data(**kwargs)
        context['offering'] = Offering.objects.filter(id=kwargs['offering']).first()
        context['subscriptions'] = Subscribe.objects.filter(course__offering=kwargs['offering']).all()
        return context

class QuarterPaymentCoursesView(TemplateView):
    template_name = 'payment/finance/courses.html'

    def get_context_data(self, **kwargs):
        context = super(QuarterPaymentCoursesView, self).get_context_data(**kwargs)
        context['offering'] = Offering.objects.filter(id=kwargs['offering']).first()
        context['subscriptions'] = Subscribe.objects.filter(course__offering=kwargs['offering']).all()
        return context
