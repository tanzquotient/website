from datetime import datetime

from cms.models.pluginmodel import CMSPlugin
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from pytz import timezone

from courses.models import LessonOccurrence, Subscribe, SubscribeState, CourseType
from courses.utils import lesson_lead_follow_balance


@plugin_pool.register_plugin
class ReplacementsPlugin(CMSPluginBase):
    name = _("Replacements")
    model = CMSPlugin
    render_template = "courses/plugins/replacements/index.html"
    text_enabled = False
    allow_children = False

    def render(self, context: dict, instance: CMSPlugin, placeholder: str) -> dict:
        user: User = context["user"]
        balances, lessons = self.lessons_and_balances()
        context["lessons"] = lessons
        context["balances"] = balances
        context["allowed_course_types"] = self.allowed_course_types(user)
        context["subscribed_courses"] = self.subscribed_courses(user)
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
