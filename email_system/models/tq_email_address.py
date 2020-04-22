from django.db.models import CharField, EmailField
from django.utils.translation import ugettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields


class TqEmailAddress(TranslatableModel):
    email_address = EmailField(blank=False)

    # Translated fields
    translations = TranslatedFields(
        description=CharField(verbose_name=_('Description'), max_length=200, blank=True, null=True),
    )

    def get_headers(self):
        return {
            'Reply-To': self.email_address,
            'From': self.email_address,
        }

    def __str__(self):
        return self.email_address

    class Meta:
        verbose_name = _('Email Address')
