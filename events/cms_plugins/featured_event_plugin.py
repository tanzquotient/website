from cms.models.pluginmodel import CMSPlugin
from cms.plugin_base import CMSPluginBase
from django.db import models
from django.utils.translation import gettext_lazy as _


class FeaturedEventPluginModel(CMSPlugin):
    event = models.ForeignKey(to='Event', on_delete=models.PROTECT, related_name='featured_plugins', blank=False)


class FeaturedEventPlugin(CMSPluginBase):
    name = _("Featured Event")
    model = FeaturedEventPluginModel
    render_template = "events/snippets/event_card.html"
    text_enabled = False
    allow_children = False

    def render(self, context, instance, placeholder):
        context.update({
            'event': instance.event,
        })
        return context
