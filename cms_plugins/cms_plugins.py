from datetime import datetime, time

from cms.models.pluginmodel import CMSPlugin
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from djangocms_text.fields import HTMLField

from courses.models import IrregularLesson, OfferingType
from events.models import Event


class PageTitlePluginModel(CMSPlugin):
    title = models.CharField(max_length=30, blank=True, null=True)
    title.help_text = (
        "The title to be displayed. Leave empty to display the page's title."
    )
    subtitle = models.CharField(max_length=50, blank=True, null=True)
    subtitle.help_text = "The subtitle to be displayed."


@plugin_pool.register_plugin
class PageTitlePlugin(CMSPluginBase):
    name = _("Page title")
    model = PageTitlePluginModel
    render_template = "plugins/page_title.html"
    text_enabled = True
    allow_children = True

    def render(self, context, instance, placeholder):
        context.update({"instance": instance})
        return context


class AlertPluginModel(CMSPlugin):
    TYPES = (
        ("primary", "Primary"),
        ("secondary", "Secondary"),
        ("success", "Success"),
        ("danger", "Danger"),
        ("warning", "Warning"),
        ("info", "Info"),
        ("light", "Light"),
        ("dark", "Dark"),
    )

    title = models.CharField(max_length=100, blank=True, null=True)
    content = HTMLField(blank=False, null=False)
    type = models.CharField(choices=TYPES, max_length=20, blank=False, null=False)


@plugin_pool.register_plugin
class AlertPlugin(CMSPluginBase):
    name = _("Alert")
    model = AlertPluginModel
    render_template = "cms_plugins/alert.html"
    text_enabled = True
    allow_children = False

    def render(self, context, instance, placeholder):
        context.update(
            {
                "title": instance.title,
                "content": instance.content,
                "type": instance.type,
            }
        )
        return context


class QuickLinksPluginModel(CMSPlugin):
    title = models.CharField(max_length=100, blank=True, null=True)
    text = models.CharField(max_length=100, blank=True, null=True)


@plugin_pool.register_plugin
class QuickLinksPlugin(CMSPluginBase):
    name = _("Quick Links")
    model = QuickLinksPluginModel
    render_template = "cms_plugins/quick_links.html"
    text_enabled = False
    allow_children = True

    def render(self, context, instance, placeholder):
        context.update(
            {
                "instance": instance,
            }
        )
        return context


class RowPluginModel(CMSPlugin):
    column_classes = models.CharField(max_length=200, blank=True, null=True)


@plugin_pool.register_plugin
class RowPlugin(CMSPluginBase):
    name = _("Row")
    render_template = "plugins/row.html"
    model = RowPluginModel

    text_enabled = True
    allow_children = True

    def render(self, context, instance, placeholder):
        context.update({"instance": instance})
        return context


class UpcomingEventsAndCoursesPluginModel(CMSPlugin):
    delta_days = models.IntegerField(blank=True, null=True)
    delta_days.help_text = (
        "Events and courses within the time delta (in days) from now on are shown."
        "Leave empty to make no restrictions."
    )
    max_displayed = models.IntegerField(blank=True, null=True)
    max_displayed.help_text = (
        "Maximum number of items to be displayed. Leave empty to make no restrictions."
    )


@plugin_pool.register_plugin
class UpcomingEventsAndCoursesPlugin(CMSPluginBase):
    name = _("Upcoming events and courses")
    model = UpcomingEventsAndCoursesPluginModel
    render_template = "cms_plugins/upcoming_events_and_courses.html"
    text_enabled = False
    allow_children = False

    def render(self, context, instance, placeholder):
        items = []

        events = (
            Event.displayed_events.future(
                delta_days=instance.delta_days, limit=instance.max_displayed
            )
            .prefetch_related("room")
            .all()
        )

        irregular_lessons = (
            IrregularLesson.objects.exclude(course__offering__type=OfferingType.PARTNER)
            .filter(date__gte=datetime.today())
            .order_by("date")
            .prefetch_related("course", "course__type", "course__room")
            .all()
        )

        for event in events:
            items.append(
                {
                    "format_duration": event.format_duration(),
                    "date": event.date,
                    "time_from": event.time_from,
                    "name": event.get_name(),
                    "special": event.special,
                    "format_prices": event.format_prices(),
                    "room": event.room,
                    "cancelled": event.cancelled,
                    "event": event,
                    "detail_url": reverse(
                        "events:detail", kwargs={"event_id": event.id}
                    ),
                }
            )

        for irregular_lesson in irregular_lessons:
            if not irregular_lesson.course.is_displayed():
                continue
            if len(irregular_lesson.course.get_lessons()) == 1:
                items.append(
                    {
                        "format_duration": irregular_lesson.format_duration(),
                        "date": irregular_lesson.date,
                        "time_from": irregular_lesson.time_from,
                        "name": irregular_lesson.course.type.title,
                        "room": irregular_lesson.course.room,
                        "special": False,
                        "format_prices": irregular_lesson.course.format_prices(),
                        "course": irregular_lesson.course,
                        "detail_url": reverse(
                            "courses:course_detail",
                            kwargs={"course_id": irregular_lesson.course.id},
                        ),
                    }
                )

        items.sort(
            key=lambda item: datetime.combine(item["date"], item["time_from"] or time())
        )
        items = items[0 : instance.max_displayed]

        context.update(
            {
                "items": items,
            }
        )
        return context
