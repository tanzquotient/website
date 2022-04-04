from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView

from courses.models import Course
from payment.views import TeacherOfCourseOnly


class CoursePaymentDetailView(TemplateView, TeacherOfCourseOnly):
    template_name = 'payment/courses/course.html'

    def get_context_data(self, **kwargs):
        course = Course.objects.filter(id=kwargs['course']).first()

        context = super(CoursePaymentDetailView, self).get_context_data(**kwargs)
        context['course'] = course
        context['description_de'] = course.safe_translation_getter('description', language_code='de')
        context['description_en'] = course.safe_translation_getter('description', language_code='en')
        context['type_description_de'] = course.type.safe_translation_getter('description', language_code='de')
        context['type_description_en'] = course.type.safe_translation_getter('description', language_code='en')
        context['participatory'] = course.subscriptions.accepted().select_related('user')
        return context

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """

        c = Course.objects.filter(id=kwargs['course']).first()
        c.set_current_language('de')
        c.description = request.POST['ckeditor-de']
        c.set_current_language('en')
        c.description = request.POST['ckeditor-en']
        c.save()

        return HttpResponseRedirect(reverse('payment:coursepayment_detail', kwargs={'course': self.kwargs['course']}))