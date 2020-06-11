from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.models.pluginmodel import CMSPlugin
from django.utils.translation import gettext_lazy as _
from django.db import models
from events.models import Event, EventCategory


class EventsPluginModel(CMSPlugin):
    title = models.CharField(blank=True, null=True, max_length=50)
    include_specials = models.BooleanField(blank=False, default=True)
    include_regular = models.BooleanField(blank=False, default=True)
    show_when_no_events = models.BooleanField(blank=False, default=False)
    style = models.IntegerField(blank=False, choices=((0, _('List')), (1, _('Cards'))), default=0)


class EventsPlugin(CMSPluginBase):
    name = _("Events")
    model = EventsPluginModel
    render_template = "events/events.html"
    text_enabled = False
    allow_children = False

    def render(self, context, instance, placeholder):
        specials = [instance.include_specials, not instance.include_regular]
        context.update({
            'events': Event.displayed_events.future().filter(special__in=specials).all(),
            'use_cards': instance.style == 1,
            'title': instance.title,
            'show_when_no_events': instance.show_when_no_events,
        })
        return context


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


plugin_pool.register_plugin(EventsPlugin)
plugin_pool.register_plugin(EventCategoryPlugin)
plugin_pool.register_plugin(FeaturedEventPlugin)
plugin_pool.register_plugin(EventsTeaserPlugin)
