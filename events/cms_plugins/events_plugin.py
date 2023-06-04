from cms.models.pluginmodel import CMSPlugin
from cms.plugin_base import CMSPluginBase
from django.db import models
from django.utils.translation import gettext_lazy as _

from events.models import Event


class EventsPluginModel(CMSPlugin):
    title = models.CharField(blank=True, null=True, max_length=50)
    include_specials = models.BooleanField(blank=False, default=True)
    include_regular = models.BooleanField(blank=False, default=True)
    show_when_no_events = models.BooleanField(blank=False, default=False)
    style = models.IntegerField(
        blank=False, choices=((0, _("List")), (1, _("Cards"))), default=0
    )


class EventsPlugin(CMSPluginBase):
    name = _("Events")
    model = EventsPluginModel
    render_template = "events/events.html"
    text_enabled = False
    allow_children = False

    def render(self, context, instance, placeholder):
        specials = [instance.include_specials, not instance.include_regular]
        context.update(
            {
                "events": Event.displayed_events.future()
                .filter(special__in=specials)
                .all(),
                "use_cards": instance.style == 1,
                "title": instance.title,
                "show_when_no_events": instance.show_when_no_events,
            }
        )
        return context
