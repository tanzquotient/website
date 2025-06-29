from datetime import datetime
from typing import Iterable

from cms.models.pluginmodel import CMSPlugin
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.contrib.auth.models import User
from django.db.models import Q, QuerySet
from django.utils.translation import gettext_lazy as _
from pytz import timezone

from ..models import SubscribeState, LessonOccurrence, AttendanceState
from ..utils import change_attendance_window_open


@plugin_pool.register_plugin
class MyNextLessonsPlugin(CMSPluginBase):
    name = _("My next lessons")
    model = CMSPlugin
    render_template = "courses/plugins/next_lessons/index.html"
    text_enabled = False
    allow_children = False
    cache = False

    def render(self, context: dict, instance: CMSPlugin, placeholder: str) -> dict:
        now = datetime.now(tz=timezone("Europe/Zurich"))
        user = context["user"]
        lessons = MyNextLessonsPlugin._get_lessons(now, user)
        courses = {lesson.course for lesson in lessons}
        context["now"] = now
        context["courses"] = courses
        context["lessons"] = lessons
        context["can_change_attendances"] = self.can_change_attendances(lessons)
        return context

    @staticmethod
    def _get_lessons(now: datetime, user: User) -> QuerySet[LessonOccurrence]:
        lessons = (
            LessonOccurrence.objects.filter(
                (
                    Q(
                        course__subscriptions__user=user,
                        course__subscriptions__state__in=SubscribeState.ACCEPTED_STATES,
                    )
                    | Q(
                        attendances__user=user,
                        attendances__state=AttendanceState.REPLACEMENT,
                    )
                )
                & Q(start__gt=now)
            )
            .prefetch_related(
                "attendances",
                "course__type__translations",
                "course__subscriptions",
            )
            .order_by("start")
            .distinct()
        )
        return lessons

    @staticmethod
    def can_change_attendances(lessons: Iterable[LessonOccurrence]) -> dict[int, bool]:
        return {lesson.id: change_attendance_window_open(lesson) for lesson in lessons}
