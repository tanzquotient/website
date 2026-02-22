from datetime import date
from typing import Optional

from django.db import models
from django.utils.translation import gettext_lazy as _
from djangocms_text.fields import HTMLField
from parler.models import TranslatableModel, TranslatedFields

from utils import TranslationUtils
from . import Address, RoomAccessCode


class Room(TranslatableModel):
    name = models.CharField(max_length=30, unique=True, blank=False)
    address = models.ForeignKey(
        to=Address,
        related_name="rooms",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )
    url = models.URLField(max_length=500, blank=True, null=True)
    url.help_text = "The url to Google Maps (see https://support.google.com/maps/answer/144361?p=newmaps_shorturl&rd=1)"
    contact_info = models.TextField(blank=True, null=True)

    translations = TranslatedFields(
        description=HTMLField(
            verbose_name="[TR] Description",
            blank=True,
            null=True,
            help_text=_(
                "Information on how to get to the room. E.g. where it is located, "
                "what entrance to use, or any additional information."
            ),
        ),
        instructions=HTMLField(
            verbose_name="[TR] Instructions",
            blank=True,
            null=True,
            help_text=_(
                "Instructions for teachers/staff. E.g. how to get access, how to use "
                "the sound system, noise regulations, etc."
            ),
        ),
        disclaimer=HTMLField(
            verbose_name="[TR] Disclaimer",
            blank=True,
            null=True,
            help_text=_(
                "Important notes for this room, that will be shown together with the "
                "course description. E.g. required ASVZ membership, notes on "
                "last minute cancellations for food&lab, etc."
            ),
        ),
        information_for_participants=HTMLField(
            verbose_name="[TR] Information for participants",
            blank=True,
            null=True,
            help_text=_(
                "Shown only to participants who are confirmed for a course in this room."
            ),
        ),
    )

    def get_description(self) -> Optional[str]:
        return TranslationUtils.get_text_with_language_fallback(self, "description")

    def get_instructions(self) -> Optional[str]:
        return TranslationUtils.get_text_with_language_fallback(self, "instructions")

    def get_disclaimer(self) -> Optional[str]:
        return TranslationUtils.get_text_with_language_fallback(self, "disclaimer")

    def get_information_for_participants(self) -> Optional[str]:
        return TranslationUtils.get_text_with_language_fallback(
            self, "information_for_participants"
        )

    def has_additional_info(self) -> bool:
        return (
            self.address
            or self.url
            or self.contact_info
            or self.get_description()
            or self.get_instructions()
        ) is not None

    def is_cancelled(self, query_date: date) -> bool:
        return any((query_date == c.date for c in self.cancellations.all()))

    def get_access_codes(
        self, code_date: date | None = None
    ) -> models.QuerySet[RoomAccessCode]:
        if code_date is None:
            code_date = date.today()
        qs: models.QuerySet[RoomAccessCode] = self.access_codes.filter(
            valid_from__lte=code_date, valid_until__gte=code_date
        )
        return qs

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["name"]
