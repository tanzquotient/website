from datetime import datetime
from typing import Iterable

from cms.models.pluginmodel import CMSPlugin
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from pytz import timezone

from courses.models import (
    LessonOccurrence,
    Subscribe,
    SubscribeState,
    CourseType,
    AttendanceState,
)
from courses.utils import lesson_lead_follow_balance, claiming_spot_window_open


@plugin_pool.register_plugin
class ReplacementsPlugin(CMSPluginBase):
    name = _("Replacements")
    model = CMSPlugin
    render_template = "courses/plugins/replacements/index.html"
    text_enabled = False
    allow_children = False
    cache = False

    def render(self, context: dict, instance: CMSPlugin, placeholder: str) -> dict:
        user: User = context["user"]
        balances, lessons = self.lessons_and_balances()
        context["lessons"] = lessons
        context["balances"] = balances
        context["allowed_course_types"] = self.allowed_course_types(user)
        context["subscribed_courses"] = self.subscribed_courses(user)
        context["claimed_spots"] = self.claimed_spots(user, lessons)
        context["claim_spots_window_open"] = self.claim_spots_window_open(lessons)
        return context

    @staticmethod
    def lessons_and_balances() -> tuple[dict[int, int], list[LessonOccurrence]]:
        lessons = (
            LessonOccurrence.objects.filter(
                start__gte=datetime.now(tz=timezone("Europe/Zurich")),
                course__type__couple_course=True,
            )
            .prefetch_related(
                "course__type__translations",
                "course__room",
                "course__subscriptions",
                "attendances",
            )
            .distinct()
        )
        balances = {
            l.id: balance
            for l in lessons
            if (balance := lesson_lead_follow_balance(l)) != 0
        }
        sorted_lessons = sorted(
            lessons,
            key=lambda l: (l.start.date(), l.course.type.title, l.start.time()),
        )
        filtered_lessons = [l for l in sorted_lessons if l.id in balances]
        return balances, filtered_lessons

    @staticmethod
    def allowed_course_types(user: User) -> set[CourseType]:
        return set(user.skill.unlocked_course_types.all())

    @staticmethod
    def subscribed_courses(user: User) -> list[int]:
        return [
            s.course_id
            for s in Subscribe.objects.filter(
                user=user, state__in=SubscribeState.ACCEPTED_STATES
            )
        ]

    @staticmethod
    def claimed_spots(
        user: User, lessons: list[LessonOccurrence]
    ) -> list[LessonOccurrence]:
        return [l for l in lessons if ReplacementsPlugin.is_replacement(user, l)]

    @staticmethod
    def is_replacement(user: User, lesson: LessonOccurrence) -> bool:
        for a in lesson.attendances.all():
            if a.user == user and a.state == AttendanceState.REPLACEMENT:
                return True
        return False

    @staticmethod
    def claim_spots_window_open(lessons: Iterable[LessonOccurrence]) -> dict[int, bool]:
        return {lesson.id: claiming_spot_window_open(lesson) for lesson in lessons}
