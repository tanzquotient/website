from django.views.generic import TemplateView

from courses.models import Course
from payment.views import TeacherOfCourseOnly


class CourseParticipantsView(TemplateView, TeacherOfCourseOnly):
    template_name = "payment/courses/participants.html"

    def get_context_data(self, **kwargs) -> dict:
        course: Course = Course.objects.filter(id=kwargs.get("course")).first()
        context = super(CourseParticipantsView, self).get_context_data(**kwargs)
        context["course"] = course
        context["participatory"] = course.subscriptions.accepted().select_related(
            "user"
        )
        return context
