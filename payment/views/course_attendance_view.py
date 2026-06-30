from datetime import datetime
from zoneinfo import ZoneInfo

from django.views.generic import TemplateView

from courses.models import (
    Course,
)
from payment.views.teachers_of_course_only import TeacherOfCourseOnly


class CourseAttendanceView(TemplateView, TeacherOfCourseOnly):
    template_name = "payment/courses/attendance.html"

    def get_context_data(self, **kwargs):
        course: Course = Course.objects.filter(id=kwargs.get("course")).first()
        context = super(CourseAttendanceView, self).get_context_data(**kwargs)
        context["course"] = course
        context["now"] = datetime.now(tz=ZoneInfo("Europe/Zurich"))
        return context
