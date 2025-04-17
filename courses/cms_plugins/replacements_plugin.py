from datetime import datetime, timedelta

from cms.models.pluginmodel import CMSPlugin
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import gettext_lazy as _
from pytz import timezone

from courses.models import LessonOccurrence


@plugin_pool.register_plugin
class ReplacementsPlugin(CMSPluginBase):
    name = _("Replacements")
    model = CMSPlugin
    render_template = "courses/plugins/replacements/index.html"
    text_enabled = False
    allow_children = False

    def render(self, context: dict, instance: CMSPlugin, placeholder: str) -> dict:
        start_from = datetime.now(tz=timezone("Europe/Zurich"))
        start_to = start_from.replace(hour=23, minute=59, second=59) + timedelta(
            days=14
        )
        lessons = (
            LessonOccurrence.objects.filter(start__gte=start_from, start__lt=start_to)
            .exclude(course__subscriptions__user=context["user"])
            .order_by("start")
        )
        return dict(lessons=lessons)
