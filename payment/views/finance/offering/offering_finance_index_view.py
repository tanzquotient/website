from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import TemplateView


class OfferingFinanceIndexView(PermissionRequiredMixin, TemplateView):
    template_name = "finance/offering/index.html"
    permission_required = "payment.change_payment"
