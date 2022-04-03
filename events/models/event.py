from typing import Optional

from django.db.models import TimeField, BooleanField, DateField, DecimalField, ForeignKey, ImageField, CharField, \
    IntegerField, SET_NULL
from django.urls import reverse
from django.utils.translation import gettext as _
from djangocms_text_ckeditor.fields import HTMLField
from parler.managers import TranslatableManager
from parler.models import TranslatableModel, TranslatedFields

from courses.models import Room
from courses.services import format_prices
from utils import TranslationUtils
from . import EventRegistration
from .. import managers


class Event(TranslatableModel):
    date = DateField()
    time_from = TimeField(blank=True, null=True)
    date_to = DateField(blank=True, null=True, help_text='If start and end are on different days')
    time_to = TimeField(blank=True, null=True)
    cancelled = BooleanField(default=False)
    category = ForeignKey('EventCategory', related_name='events', blank=True, null=True, on_delete=SET_NULL)
    room = ForeignKey(Room, related_name='events', blank=True, null=True, on_delete=SET_NULL)
    price_with_legi = DecimalField(blank=True, null=True, decimal_places=2, max_digits=6,
                                   help_text="Leave this empty for free entrance")
    price_without_legi = DecimalField(blank=True, null=True, decimal_places=2, max_digits=6,
                                      help_text="Leave this empty for free entrance")
    special = BooleanField(blank=True, default=False,
                           help_text="If this is a special event that should be emphasized on the website")
    display = BooleanField(default=True, help_text="Defines if this event should be displayed on the website.")
    image = ImageField(blank=True, null=True, help_text="Advertising image for this event.")
    registration_enabled = BooleanField(default=False,
                                        help_text="Gives participants of the event the possibility to register")
    max_participants = IntegerField(blank=True, null=True,
                                    help_text="Defines how many people can register. Leave empty for unlimited number.")

    translations = TranslatedFields(
        description=HTMLField(
            blank=True, null=True,
            verbose_name='[TR] Description'
        ),
        name=CharField(
            max_length=255, blank=False,
            verbose_name="[TR] The name of this event (e.g. 'Open Dancing')"
        ),
        price_special=CharField(
            max_length=255, blank=True, null=True,
            verbose_name="[TR] Set this only if you want a different price schema."
        ),
    )

    objects = TranslatableManager()
    displayed_events = managers.DisplayedEventManager()
    special_events = managers.SpecialEventManager()

    def format_prices(self) -> str:
        return format_prices(self.price_with_legi, self.price_without_legi, self.get_price_special())

    def format_duration(self) -> str:
        date_from = self.date
        date_to = self.date_to if self.date_to else self.date

        date_from_formatted = date_from.strftime("%a, %d.%m.%Y")
        time_from_formatted = self.time_from.strftime("%H:%M") if self.time_from else ""
        date_to_formatted = date_to.strftime("%a, %d.%m.%Y")
        time_to_formatted = self.time_to.strftime("%H:%M") if self.time_to else ""

        if date_from == date_to:
            if self.time_from and self.time_to:
                return f'{date_from_formatted}, {time_from_formatted} - {time_to_formatted}'
            if self.time_from:
                return f'{date_from_formatted}, {_("from")} {time_from_formatted}'
            return date_from_formatted

        if self.time_from and self.time_to:
            return f'{date_from_formatted} {time_from_formatted} - {date_to_formatted} {time_to_formatted}'

        return f'{date_from_formatted} - {date_to_formatted}'

    def get_name(self) -> str:
        return TranslationUtils.get_text_with_language_fallback(self, 'name')

    def get_description(self) -> str:
        return TranslationUtils.get_text_with_language_fallback(self, 'description')

    def get_price_special(self) -> str:
        return TranslationUtils.get_text_with_language_fallback(self, 'price_special')

    def free_spots(self) -> Optional[int]:
        if self.max_participants is None:
            return None
        else:
            return max(0, self.max_participants - self.registrations.count())

    def fully_booked(self) -> bool:
        if self.max_participants is None:
            return False  # There is no limit => Can not be fully booked
        return self.free_spots() <= 0

    def is_registered(self, user) -> bool:
        return user is not None and \
               not user.is_anonymous and \
               EventRegistration.objects.filter(user=user, event=self).exists()

    def registration_possible(self) -> bool:
        return self.registration_enabled and not self.fully_booked()

    def detail_url(self) -> str:
        return reverse('events:detail', kwargs={'event_id': self.id})

    def __str__(self) -> str:
        return f"{self.get_name()} ({self.date.strftime('%d.%m.%Y')})"

    class Meta:
        ordering = ['-date', '-time_from']
