from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import TemplateView

from courses.models import Offering


class OfferingFinanceIndexView(PermissionRequiredMixin, TemplateView):
    template_name = 'finance/offering/index.html'
    permission_required = 'payment.payment.change'

    def get_context_data(self, **kwargs):
        context = super(OfferingFinanceIndexView, self).get_context_data(**kwargs)
        offerings = Offering.objects.order_by('-active', '-period__date_from').all()
        context['offerings'] = offerings
        return context