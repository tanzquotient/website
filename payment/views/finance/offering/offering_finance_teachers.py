from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.http import HttpRequest, HttpResponse
from django.db.models import Q
import json

from courses.models import Offering, Course, LessonOccurrenceTeach


class OfferingFinanceTeachers(PermissionRequiredMixin, TemplateView):
    template_name = "finance/offering/teachers/index.html"

    def has_permission(self) -> bool:
        return self.request.user.has_perm(
            "payment.change_payment"
        ) or self.request.user.has_perm("courses.change_lessonoccurrence")

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        context["active"] = "teachers"
        context["offering"] = get_object_or_404(Offering, id=kwargs["offering"])
        return context

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        json_args = json.loads(request.body)
        course_id = json_args.get("course")
        fill_empty_lessons = json_args.get("fill_empty_lessons")
        query = (
            Q(offering__id=self.kwargs["offering"])
            if course_id == "all"
            else Q(id=int(course_id))
        )
        courses: list[Course] = Course.objects.filter(query).all()
        for course in courses:
            if (
                fill_empty_lessons
                and course.lesson_occurrences.without_teachers().exists()
            ):
                for l in course.lesson_occurrences.without_teachers():
                    for t in course.get_teachers():
                        LessonOccurrenceTeach.objects.create(
                            lesson_occurrence=l, teacher=t
                        )
            course.completed = True
            course.save()

        return HttpResponse(json.dumps({"result": "success"}))
