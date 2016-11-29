from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from cms.toolbar_pool import toolbar_pool
from cms.toolbar_base import CMSToolbar


@toolbar_pool.register
class CoursesToolbar(CMSToolbar):
    def populate(self):
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
        if self.request.user.has_perm('payment.change_subscriptionpayment'):
            url = reverse('admin:payment_subscriptionpayment_changelist')
            menu.add_sideframe_item(_('Subscription Payments'), url=url)
        if self.request.user.has_perm('payment.change_coursepayment'):
            url = reverse('admin:payment_coursepayment_changelist')
            menu.add_sideframe_item(_('Course Payments'), url=url)
        if self.request.user.has_perm('payment.change_paymentreminder'):
            url = reverse('admin:payment_paymentreminder_changelist')
            menu.add_sideframe_item(_('Payment Reminders'), url=url)