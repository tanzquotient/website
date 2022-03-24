from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from cms.toolbar_pool import toolbar_pool
from cms.toolbar_base import CMSToolbar


@toolbar_pool.register
class EventsToolbar(CMSToolbar):
    def populate(self) -> None:
        menu = self.toolbar.get_or_create_menu('events-app', _('Events'))
        if self.request.user.has_perm('events.change_event'):
            url = reverse('admin:events_event_changelist')
            menu.add_sideframe_item(_('Events'), url=url)
        if self.request.user.has_perm('events.change_eventregistration'):
            url = reverse('admin:events_event_eventregistration_changelist')
            menu.add_sideframe_item(_('Event Registrations'), url=url)
        if self.request.user.has_perm('events.change_eventcategory'):
            url = reverse('admin:events_event_eventcategory_changelist')
            menu.add_sideframe_item(_('Event Categories'), url=url)
