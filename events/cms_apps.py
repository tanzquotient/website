from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import gettext_lazy as _


class EventApphook(CMSApp):
    name = _("Events")
    app_name = "events"

    def get_urls(self, page=None, language=None, **kwargs):
        return ["events.urls"]


apphook_pool.register(EventApphook)
