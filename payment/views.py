import json
from datetime import date

from django import forms
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.db.models import Sum
from django.http import Http404
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.generic import TemplateView, FormView, View
from django.views.generic.edit import ProcessFormView, FormMixin

from courses.models import PaymentMethod, Offering, Voucher, Course, Teach, Subscribe
from payment import payment_processor
from payment.forms import USIForm, VoucherForm, PROG_USI, AccountFinanceIndexForm
from payment.models import Payment
from .models.choices import Type, CreditDebit
from .services import *

log = logging.getLogger('tq')


class VoucherPaymentIndexView(FormView):
    template_name = 'payment/voucher/form.html'
    form_class = VoucherForm

    def get_context_data(self, **kwargs):
        context = super(VoucherPaymentIndexView, self).get_context_data(**kwargs)

        matches = PROG_USI.match(self.kwargs['usi'])
        if not matches:
            raise Http404("USI is of invalid format")
        subscription = Subscribe.objects.filter(usi=matches.group('usi')).first()
        if not subscription:
            raise Http404("Subscription with this USI does not exist")
        context['subscription'] = subscription

        # if the user has already paid, show the payment-success view
        if subscription.paid():
            self.template_name = 'payment/voucher/payment_success.html'

        return context

    def form_valid(self, form):
        # if the user entered a valid voucher code, mark the voucher as used and redirect the user to the payment successful page

        self.success_url = reverse('payment:voucherpayment_success', kwargs={'usi': self.kwargs['usi']})

        subscription = Subscribe.objects.filter(usi=self.kwargs['usi']).first()

        voucher = Voucher.objects.filter(key=form.data['voucher_code']).first()
        if not voucher:
            raise Http404("Voucher with this code does not exist")
        if not voucher.mark_as_used(self.request.user,
                                    comment="Used to pay subscription " + payment_processor.USI_PREFIX + subscription.usi + ".",
                                    subscription=subscription):
            raise Http404("Voucher was already used")

        # show a message that the subscription has been paid (use django message passing framework)
        if subscription.apply_voucher(voucher):
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Voucher was successfully applied to Subscription") + self.kwargs['usi'])

        return super(VoucherPaymentIndexView, self).form_valid(form)


class VoucherPaymentSuccessView(TemplateView):
    def get_context_data(self, usi, **kwargs):
        subscription = Subscribe.objects.filter(usi=usi).first()

        # ensure that the payment success page is only displayed if the subscription is actually paid.
        if subscription.paid():
            self.template_name = 'payment/voucher/payment_success.html'
        else:
            self.template_name = 'payment/voucher/remaining_amount.html'

        context = super(VoucherPaymentSuccessView, self).get_context_data(**kwargs)
        context['subscription'] = subscription

        return context


class CounterPaymentIndexView(FormView):
    template_name = 'payment/counter/form.html'
    form_class = USIForm

    def form_valid(self, form):
        self.success_url = reverse('payment:counterpayment_detail', kwargs={'usi': form.cleaned_data['usi']})
        return super(CounterPaymentIndexView, self).form_valid(form)

    @method_decorator(permission_required('courses.access_counterpayment'))
    def dispatch(self, *args, **kwargs):
        return super(CounterPaymentIndexView, self).dispatch(*args, **kwargs)


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


class TeacherOnly(View):
    """
    Mixin to ensure only teachers can access a view.
    """

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        # check permissions not expressed by auth.perm
        if not self.request.user.is_staff and not self.request.user.profile.is_teacher() and not self.request.user.has_perm(
                'courses.change_subscribe'):
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
        allowed = False

        user = self.request.user
        course_id = kwargs['course']

        if user.is_superuser or user.has_perm('courses.change_subscribe'):
            allowed = True
        if user.teaching_courses.filter(course__id=course_id).exists():
            allowed = True

        if not allowed:
            raise PermissionDenied

        return super(TeacherOfCourseOnly, self).dispatch(*args, **kwargs)


class CoursePaymentIndexView(TemplateView, TeacherOnly):
    template_name = 'payment/course/form.html'

    def get_context_data(self, **kwargs):
        context = super(CoursePaymentIndexView, self).get_context_data(**kwargs)
        user = self.request.user

        tree = []
        for o in Offering.objects.order_by('-period__date_from').all():
            courses = []
            if user is not None:
                # if the user is a superuser we show him all courses, otherwise only the courses he teaches
                if user.is_superuser:
                    courses += list(o.course_set.all())
                else:
                    courses = [teach.course for teach in Teach.objects.filter(course__offering=o, teacher=user).all()]
            courses.sort(
                key=lambda
                    course: course.get_period().date_from if course.get_period() and course.get_period().date_from else datetime.date(
                    year=1990, month=
                    1, day=1), reverse=True)
            nodes = [{'text': c.name, 'href': reverse('payment:coursepayment_detail', kwargs={'course': c.id})} for c in
                     courses]
            if o.period and o.period.date_from and o.period.date_from > date.today():
                color = "#5bc0de"
            elif o.period and o.period.date_to and o.period.date_to < date.today():
                color = "#DDDDDD"
            else:
                color = "#FFFFFF"
                
            if courses:    
                tree.append({
                    'text': o.name,
                    'nodes': nodes,
                    'state': {
                        'expanded': False,
                    },
                    'selectable': False,
                    'backColor': color,
                })

        context['tree'] = json.dumps(tree)
        return context


class CoursePaymentDetailView(TemplateView, TeacherOfCourseOnly):
    template_name = 'payment/course/course.html'

    def get_context_data(self, **kwargs):
        course = Course.objects.filter(id=kwargs['course']).first()

        context = super(CoursePaymentDetailView, self).get_context_data(**kwargs)
        context['course'] = course
        context['description_de'] = course.safe_translation_getter('description', language_code='de')
        context['description_en'] = course.safe_translation_getter('description', language_code='en')
        context['type_description_de'] = course.type.safe_translation_getter('description', language_code='de')
        context['type_description_en'] = course.type.safe_translation_getter('description', language_code='en')
        context['participatory'] = course.subscriptions.accepted().select_related('user')
        return context

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """

        c = Course.objects.filter(id=kwargs['course']).first()
        c.set_current_language('de')
        c.description = request.POST['ckeditor-de']
        c.set_current_language('en')
        c.description = request.POST['ckeditor-en']
        c.save()

        return HttpResponseRedirect(reverse('payment:coursepayment_detail', kwargs={'course': self.kwargs['course']}))


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
        if subscription.mark_as_paid(PaymentMethod.COURSE, self.request.user):
            messages.add_message(self.request, messages.SUCCESS,
                                 "USI " + self.kwargs['usi'] + _(' successfully marked as paid.'))

        return super(CoursePaymentConfirm, self).form_valid(form)


class CoursePaymentExportExcel(TeacherOfCourseOnly):
    def get(self, request, *args, **kwargs):
        from courses import services
        return services.export_subscriptions([kwargs.get('course', None)], 'xlsx')


class CoursePaymentExportCsv(TeacherOfCourseOnly):
    def get(self, request, *args, **kwargs):
        from courses import services
        return services.export_subscriptions([kwargs.get('course', None)], 'csv')


class CoursePaymentExportVCard(TeacherOfCourseOnly):
    def get(self, request, *args, **kwargs):
        from courses import services
        return services.export_subscriptions([kwargs.get('course', None)], 'vcard')


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


class OfferingFinanceOverviewSubscribers(PermissionRequiredMixin, TemplateView):
    template_name = 'payment/finance/offering_overview_subscribers.html'
    permission_required = 'payment.payment.change'

    def get_context_data(self, **kwargs):
        offering = Offering.objects.get(
            id=kwargs['offering'])

        context = super(OfferingFinanceOverviewSubscribers, self).get_context_data(**kwargs)
        context['offering'] = offering
        return context


class OfferingFinanceOverviewTeachers(PermissionRequiredMixin, TemplateView):
    template_name = 'payment/finance/offering_overview_teachers.html'
    permission_required = 'payment.payment.change'

    def get_context_data(self, **kwargs):
        offering = Offering.objects.get(
            id=kwargs['offering'])

        context = super(OfferingFinanceOverviewTeachers, self).get_context_data(**kwargs)
        context['offering'] = offering
        return context


class OfferingFinanceIndexView(PermissionRequiredMixin, TemplateView):
    template_name = 'payment/finance/index.html'
    permission_required = 'payment.payment.change'

    def get_context_data(self, **kwargs):
        context = super(OfferingFinanceIndexView, self).get_context_data(**kwargs)
        offerings = Offering.objects.order_by('-active', '-period__date_from').all()
        context['offerings'] = offerings
        return context


class AccountFinanceDetailView(PermissionRequiredMixin, TemplateView, ProcessFormView, FormMixin):
    template_name = 'payment/finance/account_detail.html'
    permission_required = 'payment.payment.change'
    form_class = forms.Form

    def _filter(self):
        def to_int(s):
            if s is None:
                return None
            try:
                return int(s)
            except ValueError as e:
                return None

        year = to_int(self.request.GET.get('year'))
        month = to_int(self.request.GET.get('month'))
        filter = self.request.GET.get('filter')
        payments = Payment.objects
        if year:
            payments = payments.filter(date__year=year)
        if month:
            payments = payments.filter(date__month=month)
        if filter and filter == "true":
            filter = True
            payments = payments.exclude(
                type__in=[Type.SUBSCRIPTION_PAYMENT, Type.SUBSCRIPTION_PAYMENT_TO_REIMBURSE])
        else:
            filter = False
        return year, month, filter, payments

    def get_context_data(self, **kwargs):
        context = super(AccountFinanceDetailView, self).get_context_data(**kwargs)

        year, month, filter, payments = self._filter()

        context['filter'] = filter
        context['year'] = year
        context['month'] = month
        context['month_name'] = datetime.date(year=2000, month=int(month), day=1).strftime('%B') if month else None
        payments = payments.all()
        context['payments'] = payments
        context['total_credit'] = (
        '%.2f' % sum([p.amount for p in payments if p.credit_debit == CreditDebit.CREDIT])).replace('.',
                                                                                                            ',')  # replace function after float formatting to have decimal separator for German numbering format
        context['total_debit'] = (
        '%.2f' % sum([p.amount for p in payments if p.credit_debit == CreditDebit.DEBIT])).replace('.', ',')
        context['total_unknown'] = (
        '%.2f' % sum([p.amount for p in payments if p.credit_debit == CreditDebit.UNKNOWN])).replace('.', ',')

        # Summary
        total_subscription_payment = payments.filter(
            type__in=[Type.SUBSCRIPTION_PAYMENT,
                      Type.SUBSCRIPTION_PAYMENT_TO_REIMBURSE],
            credit_debit=CreditDebit.CREDIT).all().aggregate(Sum(
            'amount'))['amount__sum'] or 0
        total_course_payment_transfer = payments.filter(
            type__in=[Type.COURSE_PAYMENT_TRANSFER], credit_debit=CreditDebit.CREDIT).all().aggregate(
            Sum(
                'amount'))['amount__sum'] or 0
        summary = {
            'TOTAL subscription_payment': "{} CHF".format(total_subscription_payment),
            'TOTAL course_payment_transfer': "{} CHF".format(total_course_payment_transfer),
            'TOTAL subscription_payment + course_payment_transfer': "{} CHF".format(
                total_subscription_payment + total_course_payment_transfer)
        }
        context['summary'] = summary

        return context

    def post(self, request, **kwargs):

        log.debug(self.success_url)
        year, month, filter, payments = self._filter()

        self.success_url = "{}?year={}&month={}&filter={}".format(
            reverse('payment:account_finance_detail_view', kwargs=kwargs),
            year, month, filter)

        for p in payments:
            p.comment = self.request.POST['comment-{}'.format(p.id)]
            p.save()

        return super(AccountFinanceDetailView, self).post(request)


class AccountFinanceIndexView(PermissionRequiredMixin, FormView):
    template_name = 'payment/finance/account_index.html'
    permission_required = 'payment.payment.change'
    form_class = AccountFinanceIndexForm

    def get_form_kwargs(self):
        kwargs = super(AccountFinanceIndexView, self).get_form_kwargs()
        payments = Payment.objects.all()
        years = sorted(set(p.date.year for p in payments))
        kwargs.update({'years': years})
        return kwargs

    def form_valid(self, form):
        self.success_url = "{}?year={}&month={}".format(
            reverse('payment:account_finance_detail_view'),
            form.data['year'] or "None", form.data['month'] or "None")
        return super(AccountFinanceIndexView, self).form_valid(form)
