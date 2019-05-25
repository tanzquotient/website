from cms.models.pluginmodel import CMSPlugin
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.db import models
from django.utils.translation import ugettext_lazy as _
from djangocms_link.cms_plugins import LinkPlugin
from djangocms_link.models import Link
from filer.fields.image import FilerImageField


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
    image = FilerImageField(blank=True, null=True)
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
