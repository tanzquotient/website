import uuid

from django.db.models import CharField, ImageField, URLField, BooleanField
from django.utils.translation import gettext_lazy as _
from djangocms_text_ckeditor.fields import HTMLField
from parler.models import TranslatedFields, TranslatableModel

from utils import TranslationUtils


def upload_path(instance, filename):
    extension = filename.split('.')[-1]
    return f'partners/{uuid.uuid4()}.{extension}'


class Partner(TranslatableModel):
    image = ImageField(verbose_name=_('Image'), null=True, blank=True, upload_to=upload_path)
    url = URLField(blank=False, null=False)
    active = BooleanField(default=True)

    # Translated fields
    translations = TranslatedFields(
        name=CharField(verbose_name=_('Name'), max_length=100, blank=False, null=False),
        description=HTMLField(verbose_name=_('Description'), blank=True, null=True)
    )

    def __str__(self):
        return TranslationUtils.get_text_with_language_fallback(self, "name") or '<no name>'

