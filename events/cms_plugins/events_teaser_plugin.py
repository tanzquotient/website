from cms.models.pluginmodel import CMSPlugin
from cms.plugin_base import CMSPluginBase
from django.db import models
from django.utils.translation import gettext_lazy as _

from events.models import Event


class EventsTeaserPluginModel(CMSPlugin):
    delta_days = models.IntegerField(blank=True, null=True)
    delta_days.help_text ="Events within the time delta (in days) from now on are shown. Leave empty to make no restrictions."
    max_displayed = models.IntegerField(blank=True, null=True)
    max_displayed.help_text ="Maximum number of events to be displayed. Leave empty to make no restrictions."


class EventsTeaserPlugin(CMSPluginBase):
    name = _("Events Teaser")
    model = EventsTeaserPluginModel
    render_template = "events/events_teaser.html"
    text_enabled = False
    allow_children = False

    def render(self, context, instance, placeholder):
        events = Event.displayed_events.future(delta_days=instance.delta_days, limit=instance.max_displayed).all()
        context.update({
            'events': events,
        })
        return context
