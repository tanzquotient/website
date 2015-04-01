from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from cms.toolbar_pool import toolbar_pool
from cms.toolbar_base import CMSToolbar

@toolbar_pool.register
class CoursesToolbar(CMSToolbar):

    def populate(self):
        menu = self.toolbar.get_or_create_menu('courses-app', _('Courses'))
        if self.request.user.has_perm('courses.change_offering'):
            url = reverse('admin:courses_offering_changelist')
            menu.add_sideframe_item(_('Offerings'), url=url)
        if self.request.user.has_perm('courses.change_course'):
            url = reverse('admin:courses_course_changelist')
            menu.add_sideframe_item(_('Courses'), url=url)
        if self.request.user.has_perm('courses.change_subscribe'):
            url = reverse('admin:courses_subscribe_changelist')
            menu.add_sideframe_item(_('Subscriptions'), url=url)
        
        menu.add_break('courses-break')
        
        if self.request.user.has_perm('courses.change_coursetype'):
            url = reverse('admin:courses_coursetype_changelist')
            menu.add_sideframe_item(_('Course types'), url=url)
        if self.request.user.has_perm('courses.change_style'):
            url = reverse('admin:courses_style_changelist')
            menu.add_sideframe_item(_('Styles'), url=url)
        if self.request.user.has_perm('courses.change_song'):
            url = reverse('admin:courses_song_changelist')
            menu.add_sideframe_item(_('Songs'), url=url)
        if self.request.user.has_perm('courses.change_period'):
            url = reverse('admin:courses_period_changelist')
            menu.add_sideframe_item(_('Periods'), url=url)
        if self.request.user.has_perm('courses.change_room'):
            url = reverse('admin:courses_room_changelist')
            menu.add_sideframe_item(_('Rooms'), url=url)
        if self.request.user.has_perm('courses.change_address'):
            url = reverse('admin:courses_address_changelist')
            menu.add_sideframe_item(_('Addresses'), url=url)
        
        menu.add_break('courses-break2')
        
        if self.request.user.has_perm('courses.change_confirmation'):
            url = reverse('admin:courses_confirmation_changelist')
            menu.add_sideframe_item(_('Confirmations'), url=url)

