from cms.models.pluginmodel import CMSPlugin
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


class ManagingCommitteePlugin(CMSPluginBase):
    name = _("Managing Committee")
    model = CMSPlugin
    render_template = "organisation/managing_committee.html"
    text_enabled = False
    allow_children = False

    def render(self, context, instance, placeholder):
        users = (
            User.objects.filter(
                functions__isnull=False
            )
            .distinct()
            .prefetch_related(
                "profile",
                "teaching_courses",
                "teaching_courses__course",
                "teaching_courses__course__lesson_occurrences",
            )
            .order_by("first_name", "last_name")
        )

        context.update(
            {
                "users": users,
            }
        )
        return context


plugin_pool.register_plugin(ManagingCommitteePlugin)
