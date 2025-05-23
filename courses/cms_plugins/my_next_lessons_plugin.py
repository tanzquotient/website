from datetime import datetime

from cms.models.pluginmodel import CMSPlugin
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from pytz import timezone

from courses.models import SubscribeState, LessonOccurrence, AttendanceState


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
        lessons = (
            LessonOccurrence.objects.filter(
                (
                    Q(
                        course__subscriptions__user=context["user"],
                        course__subscriptions__state__in=SubscribeState.ACCEPTED_STATES,
                    )
                    | Q(
                        attendances__user=context["user"],
                        attendances__state__in=AttendanceState.REPLACEMENT_STATES,
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
        courses = {lesson.course for lesson in lessons}
        context["now"] = now
        context["courses"] = courses
        context["lessons"] = lessons
        return context
