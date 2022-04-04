from django.views.generic import TemplateView

from courses.models import Offering
from payment.views import TeacherOnly


class CoursesAsTeacherList(TemplateView, TeacherOnly):
    template_name = 'payment/courses/list.html'

    def get_context_data(self, **kwargs) -> dict:
        return dict(offerings=Offering.objects.order_by('-display', '-period__date_from').prefetch_related(
            'course_set',
            'course_set__teaching',
        ).all())
