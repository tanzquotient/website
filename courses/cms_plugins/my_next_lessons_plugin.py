from datetime import datetime

from cms.models.pluginmodel import CMSPlugin
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.db.models import Min
from django.utils.translation import gettext_lazy as _
from pytz import timezone

from courses.models import Course, SubscribeState


@plugin_pool.register_plugin
class MyNextLessonsPlugin(CMSPluginBase):
    name = _("My next lessons")
    model = CMSPlugin
    render_template = "courses/plugins/next_lessons/index.html"
    text_enabled = False
    allow_children = False

    def render(self, context: dict, instance: CMSPlugin, placeholder: str) -> dict:
        now = datetime.now(tz=timezone("Europe/Zurich"))
        courses = (
            Course.objects.filter(
                subscriptions__user=context["user"],
                subscriptions__state__in=SubscribeState.ACCEPTED_STATES,
                lesson_occurrences__start__gt=now,
            )
            .prefetch_related("lesson_occurrences__attendances")
            .annotate(start=Min("lesson_occurrences__start"))
            .order_by("start")
            .distinct()
        )
        context["now"] = now
        context["courses"] = courses
        return context
