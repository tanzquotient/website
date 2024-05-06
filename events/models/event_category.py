from typing import Iterable

from django.db.models import (
    CharField,
    BooleanField,
    QuerySet,
    PositiveSmallIntegerField,
)
from djangocms_text_ckeditor.fields import HTMLField
from parler.models import TranslatableModel, TranslatedFields
from django_resized import ResizedImageField
from django.utils.translation import gettext_lazy as _

from events.models import Event
from utils import TranslationUtils


class EventCategory(TranslatableModel):
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
        return (
            Event.displayed_events.future().filter(category=self, cancelled=False).all()
        )

    def get_next_events(self) -> Iterable[Event]:
        limit = 3
        return self.get_events().order_by("date", "time_from")[:limit]

    def get_name(self) -> str:
        return TranslationUtils.get_text_with_language_fallback(self, "name")

    def __str__(self) -> str:
        return self.get_name()

    class Meta:
        ordering = ["position"]
