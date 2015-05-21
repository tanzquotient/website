from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.models.pluginmodel import CMSPlugin
from django.utils.translation import ugettext_lazy as _
from django.db import models

from djangocms_link.models import Link
from djangocms_link.cms_plugins import LinkPlugin


class PageTitlePluginModel(CMSPlugin):
    title = models.CharField(max_length=30, blank=True, null=True)
    title.help_text = u"The title to be displayed. Leave empty to display the page's title."
    subtitle = models.CharField(max_length=50, blank=True, null=True)
    subtitle.help_text = u"The subtitle to be displayed."


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
    emphasize.help_text = u"If this button should be visually emphasized."


class ButtonPlugin(LinkPlugin):
    name = _("Button")
    model = ButtonPluginModel
    render_template = "plugins/button.html"


plugin_pool.register_plugin(PageTitlePlugin)
plugin_pool.register_plugin(ButtonPlugin)
