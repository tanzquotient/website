from django.db.models.fields import CharField
from djangocms_text_ckeditor.fields import HTMLField
from parler.models import TranslatableModel, TranslatedFields

from utils import TranslationUtils


class EventCategory(TranslatableModel):

    translations = TranslatedFields(
        name=CharField(max_length=255, blank=False, null=False),
        description=HTMLField(blank=True, null=True),
    )

    def get_name(self):
        return TranslationUtils.get_text_with_language_fallback(self, 'name')

    def __str__(self):
        return self.get_name()
