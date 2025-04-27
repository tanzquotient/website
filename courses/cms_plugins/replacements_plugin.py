from datetime import datetime, timedelta

from cms.models.pluginmodel import CMSPlugin
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import gettext_lazy as _
from pytz import timezone

from courses.models import LessonOccurrence
from courses.utils import lesson_lead_follow_balance


@plugin_pool.register_plugin
class ReplacementsPlugin(CMSPluginBase):
    name = _("Replacements")
    model = CMSPlugin
    render_template = "courses/plugins/replacements/index.html"
    text_enabled = False
    allow_children = False

    def render(self, context: dict, instance: CMSPlugin, placeholder: str) -> dict:
        allowed_course_types = context["user"].skill.unlocked_course_types.all()
        start_from = datetime.now(tz=timezone("Europe/Zurich"))
        start_to = start_from.replace(hour=23, minute=59, second=59) + timedelta(
            days=14
        )
        lessons = (
            LessonOccurrence.objects.filter(
                start__gte=start_from,
                start__lt=start_to,
                course__type__couple_course=True,
                course__type__in=allowed_course_types,
            )
            .exclude(course__subscriptions__user=context["user"])
            .prefetch_related("course__type__translations", "course__room")
            .distinct()
        )
        lessons = sorted(
            lessons,
            key=lambda l: (l.start.date(), l.course.type.title, l.start.time()),
        )
        balances = {
            l.id: balance
            for l in lessons
            if (balance := lesson_lead_follow_balance(l)) != 0
        }
        context["lessons"] = [l for l in lessons if l.id in balances]
        context["balances"] = balances
        return context
