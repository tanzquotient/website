from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
from django.urls import reverse

from courses.models import Course

class CourseTeacherPresenceView(TemplateView):
    template_name = "payment/courses/teacher_presence.html"

    def get_context_data(self, **kwargs):
        course: Course = Course.objects.filter(id=kwargs["course"]).first()

        context = super(CourseTeacherPresenceView, self).get_context_data(**kwargs)
        context["course"] = course

        return context

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """

        pass
    