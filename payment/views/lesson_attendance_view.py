from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from courses.models import (
    LessonOccurrence,
    Subscribe,
    LeadFollow,
    SubscribeState,
    AttendanceState,
)
from payment.views import TeacherOfCourseOnly


class LessonAttendanceView(TemplateView, TeacherOfCourseOnly):
    template_name = "payment/lesson/attendance.html"

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        context = super(LessonAttendanceView, self).get_context_data(**kwargs)
        lesson = get_object_or_404(LessonOccurrence, pk=kwargs.get("lesson"))
        context["lesson"] = lesson
        context["course"] = lesson.course
        attendances = sorted(
            lesson.attendances.all(),
            key=lambda a: a.user.get_full_name(),
        )
        absent = [
            attendance
            for attendance in attendances
            if attendance.state in AttendanceState.ABSENT_STATES
        ]
        absent_users = [attendance.user for attendance in absent]
        subscriptions: list[Subscribe] = sorted(
            [
                subscription
                for subscription in lesson.course.subscriptions.all()
                if subscription.state in SubscribeState.ACCEPTED_STATES
                and subscription.user not in absent_users
            ],
            key=lambda s: s.user.get_full_name(),
        )
        context["present"] = [s.user for s in subscriptions]
        context["present_leaders"] = self._by_role(subscriptions, LeadFollow.LEAD)
        context["present_followers"] = self._by_role(subscriptions, LeadFollow.FOLLOW)
        context["present_no_preference"] = self._by_role(
            subscriptions, LeadFollow.NO_PREFERENCE
        )
        context["absent"] = absent
        context["replacements"] = [
            attendance
            for attendance in attendances
            if attendance.state == AttendanceState.REPLACEMENT
        ]
        context["show_check_button"] = (
            lesson.start.date() == datetime.now(tz=ZoneInfo("Europe/Zurich")).date()
        )
        return context

    @staticmethod
    def _by_role(subscriptions: list[Subscribe], role: str) -> list[User]:
        return [s.user for s in subscriptions if s.assigned_role() == role]
