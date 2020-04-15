from django.db.models import SET_NULL, PROTECT, ForeignKey, OneToOneField, Model
from post_office.models import Email
from django.utils.translation import ugettext_lazy as _


class GeneratedTQEmail(Model):
    source = ForeignKey(to='TQEmail', related_name='generated_emails', on_delete=SET_NULL, blank=True, null=True)
    email = OneToOneField(to=Email, unique=True, related_name='generated_tq_emails', on_delete=PROTECT, blank=False)

    class Meta:
        verbose_name = _('Generated Email')