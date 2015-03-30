from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.models.pluginmodel import CMSPlugin
from django.utils.translation import ugettext_lazy as _
from django.db import models
from organisation.models import Function
    
class ManagingCommitteePlugin(CMSPluginBase):
    name = _("Managing Committee")
    model = CMSPlugin
    render_template = "organisation/managing_committee.html"
    text_enabled = False
    allow_children = False
    
    def render(self, context, instance, placeholder):
        context.update({
            'functions': Function.objects.active(),
        })
        return context

plugin_pool.register_plugin(ManagingCommitteePlugin)