from cms.models.pluginmodel import CMSPlugin
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _

from partners.models import Partner


class PartnersPlugin(CMSPluginBase):
    name = _("Partners")
    model = CMSPlugin
    render_template = "partners/partners_plugin.html"
    text_enabled = False
    allow_children = False

    def render(self, context, instance, placeholder):
        partners = Partner.objects.all()
        context.update({
            'partners': partners,
        })
        return context


plugin_pool.register_plugin(PartnersPlugin)
