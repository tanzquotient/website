from datetime import datetime

from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.api.serializers import LessonOccurrenceSerializer
from courses.models import (
    Course,
    LessonOccurrence,
    LessonOccurrenceTeach,
)
from payment.views import TeacherPresenceEnabled


class CourseTeacherPresenceView(TemplateView, TeacherPresenceEnabled, APIView):
    template_name = "payment/courses/teacher_presence.html"

    def get_context_data(self, **kwargs):
        course: Course = Course.objects.filter(id=kwargs.get("course")).first()
        course.update_lesson_occurrences()

        context = super(CourseTeacherPresenceView, self).get_context_data(**kwargs)
        context["course"] = course
        context["now"] = timezone.now()
        context["errors"] = kwargs.get("errors")
        context["success"] = kwargs.get("success")
        context["can_edit"] = self.can_edit

        return context

    def post(self, request: Request, *args, **kwargs) -> HttpResponse:
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """

        if not self.can_edit:
            raise PermissionDenied

        if request.data:
            data = request.data
            teacher_id = data.get("teacher")
            lesson_id = data.get("lesson")
            remove = data.get("action") == "remove"
            if teacher_id and lesson_id:
                lesson = LessonOccurrence.objects.get(id=lesson_id)
                if remove:
                    LessonOccurrenceTeach.objects.filter(
                        lesson_occurrence=lesson, teacher_id=teacher_id
                    ).delete()
                else:
                    LessonOccurrenceTeach.objects.get_or_create(
                        lesson_occurrence=lesson, teacher_id=teacher_id
                    )
                return Response(LessonOccurrenceSerializer(lesson).data)

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
                    if "teacher_" not in key or "_text" in key:
                        continue
                    [_, start, end, _] = key.split("_")
                    data.setdefault(f"{start}_{end}", []).append(teacher_id)
                for key, teachers in data.items():
                    if not any(teacher != "-1" for teacher in teachers):
                        messages.add_message(
                            self.request,
                            messages.ERROR,
                            "You reported no teachers for one of the lessons."
                            + " Please review your submission or contact "
                            + "Dance Administration if the lesson was cancelled.",
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
                    lesson_occurrence = LessonOccurrence.objects.get(
                        course=Course.objects.get(id=int(self.kwargs["course"])),
                        start=datetime.fromisoformat(start),
                        end=datetime.fromisoformat(end),
                    )

                    teachers = [
                        User.objects.get(id=int(user_id))
                        for user_id in teachers
                        if user_id != "-1"
                    ]
                    for teacher in teachers:
                        (
                            lesson_occurrence_teach,
                            _,
                        ) = LessonOccurrenceTeach.objects.get_or_create(
                            lesson_occurrence=lesson_occurrence, teacher=teacher
                        )
                        lesson_occurrence_teach.save()
                    LessonOccurrenceTeach.objects.filter(
                        lesson_occurrence=lesson_occurrence
                    ).exclude(teacher__in=teachers).delete()
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
