from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from cms.toolbar_pool import toolbar_pool
from cms.toolbar_base import CMSToolbar

@toolbar_pool.register
class CoursesToolbar(CMSToolbar):

    def populate(self):
        menu = self.toolbar.get_or_create_menu('courses-app', _('Courses'))
        url = reverse('admin:courses_offering_changelist')
        menu.add_sideframe_item(_('Offerings'), url=url)
        url = reverse('admin:courses_course_changelist')
        menu.add_sideframe_item(_('Courses'), url=url)
        url = reverse('admin:courses_subscribe_changelist')
        menu.add_sideframe_item(_('Subscriptions'), url=url)
        
        menu.add_break('courses-break')
        
        url = reverse('admin:courses_coursetype_changelist')
        menu.add_sideframe_item(_('Course types'), url=url)
        url = reverse('admin:courses_style_changelist')
        menu.add_sideframe_item(_('Styles'), url=url)
        url = reverse('admin:courses_song_changelist')
        menu.add_sideframe_item(_('Songs'), url=url)
        url = reverse('admin:courses_period_changelist')
        menu.add_sideframe_item(_('Periods'), url=url)
        url = reverse('admin:courses_room_changelist')
        menu.add_sideframe_item(_('Rooms'), url=url)
        url = reverse('admin:courses_address_changelist')
        menu.add_sideframe_item(_('Addresses'), url=url)
        
        menu.add_break('courses-break2')
        
        url = reverse('admin:courses_confirmation_changelist')
        menu.add_sideframe_item(_('Confirmations'), url=url)
        
        
        menu = self.toolbar.get_or_create_menu('postoffice-app', _('Email'))
        url = reverse('admin:post_office_email_changelist')
        menu.add_sideframe_item(_('Emails'), url=url)
        url = reverse('admin:post_office_emailtemplate_changelist')
        menu.add_sideframe_item(_('Email templates'), url=url)
        url = reverse('admin:post_office_log_changelist')
        menu.add_sideframe_item(_('Log'), url=url)
