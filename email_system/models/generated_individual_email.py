from django.db.models import PROTECT, SET_NULL, ForeignKey, Model, OneToOneField
from django.utils.translation import gettext_lazy as _
from post_office.models import Email

from . import GroupEmail


class GeneratedIndividualEmail(Model):
    source = ForeignKey(
        to=GroupEmail,
        related_name="generated_emails",
        on_delete=SET_NULL,
        blank=True,
        null=True,
    )
    email = OneToOneField(
        to=Email,
        unique=True,
        related_name="generated_group_emails",
        on_delete=PROTECT,
        blank=False,
    )

    class Meta:
        verbose_name = _("Generated individual Email")
