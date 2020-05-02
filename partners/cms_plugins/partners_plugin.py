from cms.models.pluginmodel import CMSPlugin
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import gettext_lazy as _
from django.utils.translation import get_language

from partners.models import Partner


class PartnersPlugin(CMSPluginBase):
    name = _("Partners")
    model = CMSPlugin
    render_template = "partners/partners_plugin.html"
    text_enabled = False
    allow_children = False

    def render(self, context, instance, placeholder):
        language = get_language()
        if language is None:
            language = 'en'
        partners = Partner.objects.translated(language).order_by('translations__name').all()
        context.update({
            'partners': partners,
        })
        return context


plugin_pool.register_plugin(PartnersPlugin)
