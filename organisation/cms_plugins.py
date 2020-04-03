from cms.models.pluginmodel import CMSPlugin
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from organisation.models import Function


class ManagingCommitteePlugin(CMSPluginBase):
    name = _("Managing Committee")
    model = CMSPlugin
    render_template = "organisation/managing_committee.html"
    text_enabled = False
    allow_children = False

    def render(self, context, instance, placeholder):

        functions = Function.objects.active()
        users = set()
        for function in functions:
            for user in function.users:
                users.add(user)

        users = list(users)

        context.update({
            'users': users,
        })
        return context


plugin_pool.register_plugin(ManagingCommitteePlugin)
