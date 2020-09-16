from django.db import models
from django.db.models.fields import BooleanField
from django.utils.translation import gettext as _
from djangocms_text_ckeditor.fields import HTMLField
from parler.managers import TranslatableManager
from parler.models import TranslatableModel, TranslatedFields

from courses.models import Room
from courses.services import format_prices, reverse
from utils import TranslationUtils
from . import EventCategory, EventRegistration
from .. import managers


class Event(TranslatableModel):
    date = models.DateField()
    time_from = models.TimeField(blank=True, null=True)
    time_to = models.TimeField(blank=True, null=True)
    category = models.ForeignKey(EventCategory, related_name='events', blank=True, null=True, on_delete=models.SET_NULL)
    cancelled = models.BooleanField(blank=False, null=False, default=False)
    room = models.ForeignKey(Room, related_name='events', blank=True, null=True, on_delete=models.SET_NULL)
    price_with_legi = models.FloatField(blank=True, null=True)
    price_with_legi.help_text = "Leave this empty for free entrance"
    price_without_legi = models.FloatField(blank=True, null=True)
    price_without_legi.help_text = "Leave this empty for free entrance"
    special = BooleanField(blank=True, null=False, default=False)
    special.help_text = "If this is a special event that should be emphasized on the website"
    display = models.BooleanField(default=True)
    display.help_text = "Defines if this event should be displayed on the website."
    image = models.ImageField(blank=True, null=True)
    image.help_text = "Advertising image for this event."
    registration_enabled = models.BooleanField(null=False, default=False)
    registration_enabled.help_text = "Gives participants of the event the possibility to reserve in advance"
    max_participants = models.IntegerField(blank=True, null=True)
    max_participants.help_text = "Defines how many people can register. Leave empty for unlimited number."

    translations = TranslatedFields(
        description=HTMLField(
            blank=True, null=True,
            verbose_name='[TR] Description'
        ),
        name=models.CharField(
            max_length=255, blank=False,
            verbose_name="[TR] The name of this event (e.g. 'Freies Tanzen')"
        ),
        price_special=models.CharField(
            max_length=255, blank=True, null=True,
            verbose_name="Set this only if you want a different price schema."
        ),
    )

    objects = TranslatableManager()
    displayed_events = managers.DisplayedEventManager()
    special_events = managers.SpecialEventManager()

    def format_prices(self):
        return format_prices(self.price_with_legi, self.price_without_legi, self.get_price_special())

    format_prices.short_description = "Prices"

    def format_time(self):
        if self.time_from and self.time_to:
            return "{}-{}".format(self.time_from.strftime("%H:%M"), self.time_to.strftime("%H:%M"))
        elif self.time_from:
            return _("from") + " {}".format(self.time_from.strftime("%H:%M"))
        else:
            return _("Time not set yet")

    format_time.short_description = "Time"

    def get_name(self):
        return TranslationUtils.get_text_with_language_fallback(self, 'name')

    def get_description(self):
        return TranslationUtils.get_text_with_language_fallback(self, 'description')

    def get_price_special(self):
        return TranslationUtils.get_text_with_language_fallback(self, 'price_special')

    def free_spots(self):
        if self.max_participants is None:
            return None
        else:
            return max(0, self.max_participants - self.registrations.count())

    def is_registered(self, user):
        return user is not None and \
               not user.is_anonymous and \
               EventRegistration.objects.filter(user=user, event=self).exists()

    def detail_url(self):
        return reverse('events:detail', kwargs={'event_id': self.id})

    def __str__(self):
        return "{}".format(self.get_name())

    class Meta:
        ordering = ['-date', '-time_from']

