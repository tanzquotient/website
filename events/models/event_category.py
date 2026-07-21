from typing import Iterable

from django.db.models import (
    BooleanField,
    CharField,
    PositiveSmallIntegerField,
    QuerySet,
)
from django.utils.translation import gettext_lazy as _
from django_resized import ResizedImageField
from djangocms_text.fields import HTMLField
from parler.models import TranslatableModel, TranslatedFields

from events.models import Event
from utils import TranslationUtils


class EventCategory(TranslatableModel):
    NEXT_EVENTS_LIMIT = 3

    is_featured = BooleanField(default=False)
    image = ResizedImageField(
        blank=True,
        null=True,
        size=[720, 405],
        crop=["middle", "center"],
        quality=75,
        help_text=_(
            "Will be center cropped and rescaled to 720x405px (16:9) upon upload."
        ),
    )
    position = PositiveSmallIntegerField("Position", default=0)
    translations = TranslatedFields(
        name=CharField(max_length=255, blank=False, null=False),
        teaser=CharField(max_length=400, blank=True, null=True),
        description=HTMLField(blank=True, null=True),
    )

    def get_events(self) -> QuerySet[Event]:
        return Event.displayed_events.future().filter(category=self).all()

    def get_next_events(self, limit: int | None = NEXT_EVENTS_LIMIT) -> Iterable[Event]:
        queryset = self.get_events().order_by("date", "time_from")
        return queryset[:limit] if limit is not None else queryset

    def get_events_visible_to(self, user) -> QuerySet[Event]:
        return self.get_events().visible_to(user)

    def get_next_events_visible_to(self, user) -> Iterable[Event]:
        return self.get_next_events(limit=None).visible_to(user)[
            : self.NEXT_EVENTS_LIMIT
        ]

    def get_name(self) -> str:
        return TranslationUtils.get_text_with_language_fallback(self, "name")

    def get_teaser(self) -> str:
        return TranslationUtils.get_text_with_language_fallback(self, "teaser")

    def get_description(self) -> str:
        return TranslationUtils.get_text_with_language_fallback(self, "description")

    def __str__(self) -> str:
        return self.get_name()

    class Meta:
        ordering = ["position"]
        verbose_name_plural = _("event categories")
