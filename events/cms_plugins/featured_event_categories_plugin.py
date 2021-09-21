from cms.models.pluginmodel import CMSPlugin
from cms.plugin_base import CMSPluginBase
from django.utils.translation import gettext_lazy as _

from events.models import EventCategory


class FeaturedEventCategoriesPluginModel(CMSPlugin):
    pass


class FeaturedEventCategoriesPlugin(CMSPluginBase):
    name = _("Featured Event Categories")
    model = FeaturedEventCategoriesPluginModel
    render_template = "events/snippets/featured_categories.html"
    text_enabled = False
    allow_children = False

    def render(self, context, instance, placeholder):
        context.update({
            'categories': EventCategory.objects.filter(is_featured=True),
        })
        return context
