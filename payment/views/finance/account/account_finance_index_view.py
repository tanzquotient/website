from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import FormView

from payment.forms import AccountFinanceIndexForm
from payment.models import Payment


class AccountFinanceIndexView(PermissionRequiredMixin, FormView):
    template_name = "finance/account/index.html"
    permission_required = "payment.change_payment"
    form_class = AccountFinanceIndexForm

    def get_form_kwargs(self):
        kwargs = super(AccountFinanceIndexView, self).get_form_kwargs()
        payments = Payment.objects.all()
        years = sorted(set(p.date.year for p in payments))
        kwargs.update({"years": years})
        return kwargs

    def form_valid(self, form):
        self.success_url = "{}?year={}&month={}".format(
            reverse("payment:account_finance_detail_view"),
            form.data["year"] or "None",
            form.data["month"] or "None",
        )
        return super(AccountFinanceIndexView, self).form_valid(form)
