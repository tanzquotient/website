from dataclasses import dataclass
from datetime import timedelta, datetime
from typing import Any, Optional
from zoneinfo import ZoneInfo

from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView

from courses.models import (
    LessonOccurrence,
    Subscribe,
    SubscribeState,
    AttendanceState,
    Attendance,
    LeadFollow,
)
from payment.views import TeacherOfCourseOnly


@dataclass(kw_only=True, frozen=True)
class CheckItem:
    user: User
    present: Optional[bool]
    is_replacement: bool
    is_excused: bool = False


class LessonAttendanceCheckView(TemplateView, TeacherOfCourseOnly):
    template_name = "payment/lesson/attendance_check.html"

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        context = super(LessonAttendanceCheckView, self).get_context_data(**kwargs)
        lesson = get_object_or_404(LessonOccurrence, pk=kwargs.get("lesson"))
        context["lesson"] = lesson
        context["course"] = lesson.course
        context["check_period_open"] = self.check_period_open(lesson)
        attendances = list(lesson.attendances.all())
        subscriptions: list[Subscribe] = [
            subscription
            for subscription in lesson.course.subscriptions.all()
            if subscription.state in SubscribeState.ACCEPTED_STATES
        ]
        absent = [
            a.user for a in attendances if a.state in AttendanceState.ABSENT_STATES
        ]
        present = [
            a.user for a in attendances if a.state in AttendanceState.PRESENT_STATES
        ]
        replacements = [
            a.user for a in attendances if a.state == AttendanceState.REPLACEMENT
        ]
        excused = [
            a.user for a in attendances if a.state == AttendanceState.ABSENT_EXCUSED
        ]

        def is_present(user: User) -> Optional[bool]:
            if user in present:
                return True
            if user in absent:
                return False
            return None

        users = set([s.user for s in subscriptions] + [a.user for a in attendances])
        context["check_list"] = sorted(
            [
                CheckItem(
                    user=u,
                    present=is_present(u),
                    is_replacement=u in replacements,
                    is_excused=u in excused,
                )
                for u in users
            ],
            key=lambda c: c.user.get_full_name(),
        )
        return context

    @staticmethod
    def check_period_open(lesson: LessonOccurrence) -> bool:
        now = datetime.now(tz=ZoneInfo("Europe/Zurich"))
        grace_period = timedelta(minutes=15)
        if now + grace_period < lesson.start:
            return False  # Too early
        if now - timedelta(minutes=30) > lesson.end:
            return False  # Too late
        return True

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        lesson = get_object_or_404(LessonOccurrence, pk=kwargs.get("lesson"))

        # Parse post content, format is {user_id: "present"/"absent"}
        presence: dict[int, bool] = {}
        for key, value in request.POST.items():
            if not key.isdigit():
                continue
            if value not in ["present", "absent"]:
                continue
            presence[int(key)] = value == "present"

        existing_attendances = {a.user.id: a for a in lesson.attendances.all()}
        course = lesson.course
        roles = {s.user.id: s.assigned_role() for s in course.subscriptions.all()}

        # Persist attendance
        for user_id, is_present in presence.items():
            attendance = existing_attendances.get(user_id)
            role = roles.get(user_id)
            self.update_attendance(attendance, role, is_present, lesson, user_id)

        overview_page = reverse(
            "payment:lesson_attendance",
            kwargs={"lesson": lesson.pk},
        )
        return HttpResponseRedirect(overview_page)

    @staticmethod
    def update_attendance(
        existing_attendance: Optional[Attendance],
        role: Optional[LeadFollow],
        is_present: bool,
        lesson: LessonOccurrence,
        user_id: int,
    ):
        if existing_attendance is None:
            Attendance.objects.create(
                lesson_occurrence=lesson,
                user_id=user_id,
                role=role,
                state=(
                    AttendanceState.PRESENT
                    if is_present
                    else AttendanceState.ABSENT_NOT_EXCUSED
                ),
            )
            return

        if is_present == (existing_attendance.state in AttendanceState.PRESENT_STATES):
            return  # Nothing to do, state already correctly represented

        # Update existing attendance
        existing_attendance.state = (
            AttendanceState.PRESENT
            if is_present
            else AttendanceState.ABSENT_NOT_EXCUSED
        )
        existing_attendance.save()
