from django.contrib.auth.decorators import permission_required
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import FormView

from payment.forms import USIForm


class CounterPaymentIndexView(FormView):
    template_name = 'payment/counter/form.html'
    form_class = USIForm

    def form_valid(self, form):
        self.success_url = reverse('payment:counterpayment_detail', kwargs={'usi': form.cleaned_data['usi']})
        return super(CounterPaymentIndexView, self).form_valid(form)

    @method_decorator(permission_required('courses.access_counterpayment'))
    def dispatch(self, *args, **kwargs):
        return super(CounterPaymentIndexView, self).dispatch(*args, **kwargs)