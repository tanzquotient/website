from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import TemplateView

from courses.models import Offering


class OfferingFinanceOverviewTeachers(PermissionRequiredMixin, TemplateView):
    template_name = 'payment/finance/offering_overview_teachers.html'
    permission_required = 'payment.payment.change'

    def get_context_data(self, **kwargs):
        offering = Offering.objects.get(
            id=kwargs['offering'])

        context = super(OfferingFinanceOverviewTeachers, self).get_context_data(**kwargs)
        context['offering'] = offering
        return context