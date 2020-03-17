from datetime import datetime

from cms.models.pluginmodel import CMSPlugin
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.db import models
from django.utils.translation import ugettext_lazy as _
from djangocms_link.cms_plugins import LinkPlugin
from djangocms_link.models import Link

from courses.models import IrregularLesson
from events.models import Event


class PageTitlePluginModel(CMSPlugin):
    title = models.CharField(max_length=30, blank=True, null=True)
    title.help_text = "The title to be displayed. Leave empty to display the page's title."
    subtitle = models.CharField(max_length=50, blank=True, null=True)
    subtitle.help_text = "The subtitle to be displayed."


class PageTitlePlugin(CMSPluginBase):
    name = _("Page title")
    model = PageTitlePluginModel
    render_template = "plugins/page_title.html"
    text_enabled = True
    allow_children = True

    def render(self, context, instance, placeholder):
        context.update({
            'instance': instance
        })
        return context


class ButtonPluginModel(Link):
    emphasize = models.BooleanField(blank=False, null=False, default=False)
    emphasize.help_text = "If this button should be visually emphasized."


class ButtonPlugin(LinkPlugin):
    name = _("Button")
    model = ButtonPluginModel
    render_template = "plugins/button.html"


class RowPlugin(CMSPluginBase):
    name = _("Row")
    render_template = "plugins/row.html"

    text_enabled = True
    allow_children = True

    def render(self, context, instance, placeholder):
        context.update({
            'instance': instance
        })
        return context


class ThumbnailPluginModel(CMSPlugin):
    image = models.ImageField(blank=True, null=True)
    image.help_text = "Image to show thumbnail for."
    crop = models.BooleanField(blank=True, null=False, default=False)
    crop.help_text = "If this thumbnail should be cropped to fit given size."
    url = models.URLField(max_length=500, blank=True, null=True)
    url.help_text = "URL to display on image click."


class ThumbnailPlugin(CMSPluginBase):
    name = _("Thumbnail")
    model = ThumbnailPluginModel
    render_template = "plugins/thumbnail.html"

    text_enabled = True
    allow_children = True

    def render(self, context, instance, placeholder):
        context.update({
            'instance': instance
        })
        return context


class UpcomingEventsAndCoursesPluginModel(CMSPlugin):
    delta_days = models.IntegerField(blank=True, null=True)
    delta_days.help_text = "Events and courses within the time delta (in days) from now on are shown." \
                           "Leave empty to make no restrictions."
    max_displayed = models.IntegerField(blank=True, null=True)
    max_displayed.help_text = "Maximum number of items to be displayed. Leave empty to make no restrictions."


class UpcomingEventsAndCoursesPlugin(CMSPluginBase):
    name = _("Upcoming events and courses")
    model = UpcomingEventsAndCoursesPluginModel
    render_template = "cms_plugins/upcoming_events_and_courses.html"
    text_enabled = False
    allow_children = False

    def render(self, context, instance, placeholder):
        items = []

        events = Event.displayed_events \
            .future(delta_days=instance.delta_days, limit=instance.max_displayed) \
            .prefetch_related('room') \
            .all()

        irregular_lessons = IrregularLesson.objects \
            .filter(date__gte=datetime.today()) \
            .order_by('date') \
            .prefetch_related('course', 'course__type', 'course__room') \
            .all()

        for event in events:
            items.append({
                'date': event.date,
                'time_from': event.time_from,
                'time_to': event.time_to,
                'name': event.get_name(),
                'special': event.special,
                'price': event.format_prices(),
                'room': event.room,
                'cancelled': event.cancelled,
                'event': event,
            })

        for irregular_lesson in irregular_lessons:
            if len(irregular_lesson.course.get_lessons()) == 1:
                items.append({
                    'date': irregular_lesson.date,
                    'time_from': irregular_lesson.time_from,
                    'time_to': irregular_lesson.time_to,
                    'name': irregular_lesson.course.type.name,
                    'room': irregular_lesson.course.room,
                    'special': False,
                    'price': irregular_lesson.course.format_prices(),
                    'course': irregular_lesson.course
                })

        items.sort(key=lambda item: datetime.combine(item["date"], item["time_from"]))
        items = items[0:instance.max_displayed]

        context.update({
            'items': items,
        })
        return context


class CountdownPluginModel(CMSPlugin):
    text = models.TextField(max_length=255, blank=True, null=True)
    finish_text = models.CharField(max_length=255, blank=True, null=True)
    finish_datetime = models.DateTimeField()
    finish_datetime.help_text = "Countdown finish date and time."
    hide = models.BooleanField(default=True)
    hide.help_text = "Hide Countdown after finished."


class CountdownPlugin(CMSPluginBase):
    name = _("Countdown")
    model = CountdownPluginModel
    render_template = "plugins/countdown.html"

    text_enabled = True

    def render(self, context, instance, placeholder):
        context.update({
            'instance': instance
        })
        return context


plugin_pool.register_plugin(PageTitlePlugin)
plugin_pool.register_plugin(ButtonPlugin)
plugin_pool.register_plugin(RowPlugin)
plugin_pool.register_plugin(ThumbnailPlugin)
plugin_pool.register_plugin(CountdownPlugin)
plugin_pool.register_plugin(UpcomingEventsAndCoursesPlugin)
