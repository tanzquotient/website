from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from courses.models import Offering


class OfferingFinanceCourses(PermissionRequiredMixin, TemplateView):
    template_name = "finance/offering/courses/index.html"
    permission_required = "payment.change_payment"

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        context["active"] = "courses"
        context["offering"] = get_object_or_404(Offering, id=kwargs["offering"])
        return context
