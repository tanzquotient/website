from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import gettext_lazy as _


class CourseApphook(CMSApp):
    name = _("Course Administration")
    app_name = "courses"

    def get_urls(self, page=None, language=None, **kwargs):
        return ["courses.urls"]


apphook_pool.register(CourseApphook)
