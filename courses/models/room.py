from django.db import models
from djangocms_text_ckeditor.fields import HTMLField
from parler.models import TranslatableModel, TranslatedFields

from . import Address


class Room(TranslatableModel):
    name = models.CharField(max_length=30, unique=True, blank=False)
    address = models.OneToOneField(Address, blank=True, null=True, on_delete=models.PROTECT)
    url = models.URLField(max_length=500, blank=True, null=True)
    url.help_text = "The url to Google Maps (see https://support.google.com/maps/answer/144361?p=newmaps_shorturl&rd=1)"
    contact_info = models.TextField(blank=True, null=True)

    translations = TranslatedFields(
        description=HTMLField(verbose_name='[TR] Description', blank=True, null=True),
        instructions=models.TextField(verbose_name='[TR] Instructions', blank=True, null=True,
                                      help_text="Instructions to prepare the room (for teachers/staff only)")
    )

    def __str__(self):
        return "{}".format(self.name)
