from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.http import HttpRequest, HttpResponse
from django.db.models import Q
import json

from courses.models import Offering, Course


class OfferingFinanceTeachers(PermissionRequiredMixin, TemplateView):
    template_name = "finance/offering/teachers/index.html"
    permission_required = "payment.change_payment"

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        context["active"] = "teachers"
        context["offering"] = get_object_or_404(Offering, id=kwargs["offering"])
        return context

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        course_id = json.loads(request.body).get("course")
        query = (
            Q(offering__id=self.kwargs["offering"])
            if course_id == "all"
            else Q(id=int(course_id))
        )
        courses: list[Course] = Course.objects.filter(query).all()
        for course in courses:
            course.completed = True
            course.save()

        return HttpResponse(json.dumps({"result": "success"}))
