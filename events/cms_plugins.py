from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.models.pluginmodel import CMSPlugin
from django.utils.translation import ugettext_lazy as _
from django.db import models
from events.models import Event

class EventsPlugin(CMSPluginBase):
    name = _("Events")
    model = CMSPlugin
    render_template = "events/events.html"
    
    def render(self, context, instance, placeholder):
        context.update({
            'events': Event.displayed_events.future().all(),
        })
        return context
    
class EventsTeaserPluginModel(CMSPlugin):
    delta_days = models.IntegerField(blank=True, null=True)
    delta_days.help_text=u"Events within the time delta (in days) from now on are shown. Leave empty to make no restrictions."
    max_displayed = models.IntegerField(blank=True, null=True)
    max_displayed.help_text=u"Maximum number of events to be displayed. Leave empty to make no restrictions."
    
class EventsTeaserPlugin(CMSPluginBase):
    name = _("Events Teaser")
    model = EventsTeaserPluginModel
    render_template = "events/events_teaser.html"
    def render(self, context, instance, placeholder):
        events=Event.displayed_events.future(instance.delta_days).all()
        if instance.max_displayed:
            events=events[0:instance.max_displayed]
        context.update({
            'events': events,
        })
        return context
    
plugin_pool.register_plugin(EventsPlugin)
plugin_pool.register_plugin(EventsTeaserPlugin)