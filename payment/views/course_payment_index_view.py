import datetime
import json
from datetime import date

from django.urls import reverse
from django.views.generic import TemplateView

from courses.models import Offering, Teach
from payment.views import TeacherOnly


class CoursePaymentIndexView(TemplateView, TeacherOnly):
    template_name = 'payment/course/form.html'

    def get_context_data(self, **kwargs):
        context = super(CoursePaymentIndexView, self).get_context_data(**kwargs)
        user = self.request.user

        tree = []
        for o in Offering.objects.order_by('-period__date_from').all():
            courses = []
            if user is not None:
                # if the user is a superuser we show him all courses, otherwise only the courses he teaches
                if user.is_superuser:
                    courses += list(o.course_set.all())
                else:
                    courses = [teach.course for teach in Teach.objects.filter(course__offering=o, teacher=user).all()]
            courses.sort(
                key=lambda
                    course: course.get_period().date_from if course.get_period() and course.get_period().date_from else datetime.date(
                    year=1990, month=
                    1, day=1), reverse=True)
            nodes = [{'text': c.name, 'href': reverse('payment:coursepayment_detail', kwargs={'course': c.id})} for c in
                     courses]
            if o.period and o.period.date_from and o.period.date_from > date.today():
                color = "#5bc0de"
            elif o.period and o.period.date_to and o.period.date_to < date.today():
                color = "#DDDDDD"
            else:
                color = "#FFFFFF"

            if courses:
                tree.append({
                    'text': o.name,
                    'nodes': nodes,
                    'state': {
                        'expanded': False,
                    },
                    'selectable': False,
                    'backColor': color,
                })

        context['tree'] = json.dumps(tree)
        return context