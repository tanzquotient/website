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

        if self.request.user.has_perm('courses.change_rejection'):
            url = reverse('admin:courses_rejection_changelist')
            menu.add_sideframe_item(_('Rejections'), url=url)

        menu = self.toolbar.get_or_create_menu('tools', _('Tools'))
        url = reverse('duplicate_users')
        menu.add_modal_item(_('Merge duplicate users'), url=url)
        url = reverse('confirmation_check')
        menu.add_modal_item(_('Check confirmations'), url=url)

        menu = self.toolbar.get_or_create_menu('payment', _('Payment'))
        if self.request.user.has_perm('courses.change_voucher'):
            url = reverse('admin:courses_voucher_changelist')
            menu.add_sideframe_item(_('Voucher'), url=url)
        if self.request.user.has_perm('courses.change_voucher_purpose'):
            url = reverse('admin:courses_voucherpurpose_changelist')
            menu.add_sideframe_item(_('Voucher purposes'), url=url)
        if self.request.user.has_perm('courses.change_voucher'):
            url = reverse('courses:voucher_generation')
            menu.add_sideframe_item(_('Generate multiple vouchers'), url=url)
        menu.add_break('payment-break')
        if self.request.user.has_perm('payment.change_payment'):
            url = reverse('admin:payment_payment_changelist')
            menu.add_sideframe_item(_('Online Payments'), url=url)

