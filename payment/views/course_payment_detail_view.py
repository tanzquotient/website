from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
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

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """

        course = Course.objects.filter(id=kwargs['course']).first()
        for language in ['de', 'en']:
            key = f"description-{language}"
            if key in request.POST:
                course.set_current_language(language)
                course.description = request.POST[key]

        course.save()

        return HttpResponseRedirect(reverse('payment:coursepayment_detail', kwargs={'course': self.kwargs['course']}))