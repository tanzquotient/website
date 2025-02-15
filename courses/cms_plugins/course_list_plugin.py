from cms.models.pluginmodel import CMSPlugin
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import gettext_lazy as _

from ..views import course_list_context


@plugin_pool.register_plugin
class CourseListPlugin(CMSPluginBase):
    name = _("Course List")
    model = CMSPlugin
    render_template = "courses/plugins/course_list.html"
    text_enabled = False
    allow_children = False

    def render(self, context: dict, instance: CMSPlugin, placeholder: str) -> dict:
        return course_list_context()
