from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _


class CourseApphook(CMSApp):
    name = _("Course Administration")
    urls = ["courses.urls"]
    app_name = "courses"


apphook_pool.register(CourseApphook)
