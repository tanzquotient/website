from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.models.pluginmodel import CMSPlugin
from django.utils.translation import ugettext_lazy as _
from django.db import models

from courses.models import Style


class MusicPluginModel(CMSPlugin):
    styles = models.ManyToManyField(Style, blank=True)
    styles.help_text = u"Styles to be displayed in this plugin. Leave empty to show all styles."


class MusicPlugin(CMSPluginBase):
    name = _("Music of dance styles")
    model = MusicPluginModel
    render_template = "courses/music.html"
    text_enabled = False
    allow_children = False

    def render(self, context, instance, placeholder):
        context.update({
            'styles': instance.styles.all() if instance.styles.count() else Style.objects.all()
        })
        return context


plugin_pool.register_plugin(MusicPlugin)
