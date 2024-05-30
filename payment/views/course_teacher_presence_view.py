from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from datetime import datetime
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied

from courses.models import Course, LessonOccurrence
from payment.views import TeacherPresenceEnabled


class CourseTeacherPresenceView(TemplateView, TeacherPresenceEnabled):
    template_name = "payment/courses/teacher_presence.html"

    def get_context_data(self, **kwargs):
        course: Course = Course.objects.filter(id=kwargs.get("course")).first()

        context = super(CourseTeacherPresenceView, self).get_context_data(**kwargs)
        context["course"] = course
        context["now"] = timezone.now()
        context["errors"] = kwargs.get("errors")
        context["success"] = kwargs.get("success")
        context["can_edit"] = self.can_edit

        return context

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """

        if not self.can_edit:
            raise PermissionDenied

        if "submit" in request.POST:
            if "" in list(request.POST.values()):
                # some teacher has not been selected
                messages.add_message(
                    self.request,
                    messages.ERROR,
                    "Please fill in the form for all past lessons.",
                    extra_tags="alert-danger",
                )
            else:
                data = {}
                for key, teacher_id in request.POST.items():
                    if "teacher_" not in key:
                        continue
                    [_, start, end, _] = key.split("_")
                    data.setdefault(f"{start}_{end}", []).append(teacher_id)
                for key, teachers in data.items():
                    if not any(teacher != "-1" for teacher in teachers):
                        messages.add_message(
                            self.request,
                            messages.ERROR,
                            "You reported no teachers for one of the lessons." +
                            " Please review your submission or contact " + 
                            "Dance Administration if the lesson was cancelled.",
                            extra_tags="alert-danger",
                        )
                        break
                    if len(teachers) != len(set(teachers)):
                        messages.add_message(
                            self.request,
                            messages.ERROR,
                            'You provided the same teacher twice for the same lesson. Setting the duplicate to "No teacher".',
                            extra_tags="alert-warning",
                        )

                    [start, end] = key.split("_")
                    lesson_occurrence, _ = LessonOccurrence.objects.get_or_create(
                        course=Course.objects.get(id=int(self.kwargs["course"])),
                        start=datetime.fromisoformat(start),
                        end=datetime.fromisoformat(end),
                    )

                    lesson_occurrence.teachers.clear()
                    lesson_occurrence.teachers.add(
                        *[
                            User.objects.get(id=int(user_id))
                            for user_id in teachers
                            if user_id != "-1"
                        ]
                    )
                    lesson_occurrence.save()
                messages.add_message(
                    self.request,
                    messages.SUCCESS,
                    "Your submission has been acquired successfully. Thank you.",
                    extra_tags="alert-success",
                )

        return HttpResponseRedirect(
            reverse(
                "payment:course_teacher_presence",
                kwargs={"course": self.kwargs["course"]},
            )
        )
