from cms.models.pluginmodel import CMSPlugin
from cms.plugin_base import CMSPluginBase
from django.db import models
from django.utils.translation import gettext_lazy as _

from events.models import Event, EventCategory


class EventCategoryPluginModel(CMSPlugin):
    category = models.ForeignKey(
        to=EventCategory,
        related_name='plugins',
        blank=False,
        null=False,
        on_delete=models.CASCADE
    )


class EventCategoryPlugin(CMSPluginBase):
    name = _("Event Category")
    model = EventCategoryPluginModel
    render_template = "events/events.html"
    text_enabled = False
    allow_children = False

    def render(self, context, instance, placeholder):
        context.update({
            'events': Event.displayed_events.future().filter(category=instance.category).all(),
            'use_cards': False,
            'title': instance.category.name,
            'text': instance.category.description,
            'show_when_no_events': True,
        })
        return context
