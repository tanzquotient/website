from cms.models.pluginmodel import CMSPlugin
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import gettext_lazy as _

from organisation.models import Function


class ManagingCommitteePlugin(CMSPluginBase):
    name = _("Managing Committee")
    model = CMSPlugin
    render_template = "organisation/managing_committee.html"
    text_enabled = False
    allow_children = False

    def render(self, context, instance, placeholder):
        users = set()
        for function in Function.objects.all():
            for user in function.users.all():
                users.add(user)

        users = sorted(users, key=lambda u: u.get_full_name())

        context.update(
            {
                "users": users,
            }
        )
        return context


plugin_pool.register_plugin(ManagingCommitteePlugin)
