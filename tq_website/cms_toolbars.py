from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
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

        menu = self.toolbar.get_or_create_menu('email', _('Email'))
        if self.request.user.has_perm('post_office.change_email'):
            url = reverse('admin:post_office_email_changelist')
            menu.add_sideframe_item(_('Emails'), url=url)
        if self.request.user.has_perm('post_office.change_emailtemplate'):
            url = reverse('admin:post_office_emailtemplate_changelist')
            menu.add_sideframe_item(_('Email templates'), url=url)
        if self.request.user.has_perm('post_office.change_log'):
            url = reverse('admin:post_office_log_changelist')
            menu.add_sideframe_item(_('Log'), url=url)

        menu.add_break('email-break')

        # submenu for newsletter
        submenu = menu.get_or_create_menu('newsletter', _('Newsletter'))
        url = reverse('newsletter_list')
        submenu.add_modal_item(_('Show subscriptions'), url=url)

        url = reverse('no_newsletter_list')
        submenu.add_modal_item(_('Show non-subscriptions'), url=url)

        # submenu for wiling to get involved
        submenu = menu.get_or_create_menu('get_involved', _('Willing to get involved'))
        url = reverse('get_involved_list')
        submenu.add_modal_item(_('Show subscriptions'), url=url)

        url = reverse('not_get_involved_list')
        submenu.add_modal_item(_('Show non-subscriptions'), url=url)

        if self.request.user.has_perm('filer.change_folder'):
            menu = self.toolbar.get_or_create_menu('files', _('Files'))
            url = reverse('admin:filer_folder_changelist')
            menu.add_modal_item(_('Files'), url=url)
