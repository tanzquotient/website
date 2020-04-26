from cms.models.pluginmodel import CMSPlugin
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _

from courses import services
from courses.models import Offering, OfferingType


class PartnerOfferingsPlugin(CMSPluginBase):
    name = _("Partner Offerings")
    model = CMSPlugin
    render_template = "partners/partner_offerings_plugin.html"
    text_enabled = False
    allow_children = False

    def render(self, context, instance, placeholder):
        offerings = [
            {
                'offering': offering,
                'sections': services.get_sections(offering)
            }
            for offering in Offering.objects.filter(type=OfferingType.PARTNER, display=True)
        ]
        context.update({
            'offerings': offerings,
            'hide_title': len(offerings) <= 1
        })
        return context


plugin_pool.register_plugin(PartnerOfferingsPlugin)
