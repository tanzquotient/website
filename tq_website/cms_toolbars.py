from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from cms.toolbar_pool import toolbar_pool
from cms.toolbar_base import CMSToolbar


@toolbar_pool.register
class OrganisationToolbar(CMSToolbar):
    def populate(self):
        menu = self.toolbar.get_or_create_menu('organisation-app', _('Organisation'))
        if self.request.user.has_perm('organisation.change_function'):
            url = reverse('admin:organisation_function_changelist')
            menu.add_sideframe_item(_('Association functions'), url=url)

        menu.add_break('organisation-break')

        if self.request.user.has_perm('faq.change_questiongroup'):
            url = reverse('admin:faq_questiongroup_changelist')
            menu.add_sideframe_item(_('FAQ - Question groups'), url=url)
