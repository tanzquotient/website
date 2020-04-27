from django.contrib.auth.models import Group
from django.db.models import SET_NULL, ForeignKey, DateTimeField, CharField
from django.utils.translation import ugettext_lazy as _
from djangocms_text_ckeditor.fields import HTMLField
from parler.models import TranslatedFields, TranslatableModel

from utils import TranslationUtils


class GroupEmail(TranslatableModel):
    target_group = ForeignKey(verbose_name=_('Target group'), to=Group, related_name='tq_emails', on_delete=SET_NULL, blank=True, null=True)
    reply_to = ForeignKey(verbose_name=_('Reply-To address'), to='TqEmailAddress', related_name='group_email_reply_tos', on_delete=SET_NULL, blank=True, null=True)
    sent_at = DateTimeField(null=True, blank=True)

    # Translated fields
    translations = TranslatedFields(
        subject=CharField(verbose_name=_('Subject'), max_length=100, blank=False),
        message=HTMLField(verbose_name=_('Message'), blank=False, help_text=_('Content of the email'))
    )

    def is_sent(self):
        return self.sent_at is not None

    def get_recipients(self):
        return self.target_group.user_set.all()

    def __str__(self):
        return TranslationUtils.get_text_with_language_fallback(self, "subject") or '<no subject>'

    class Meta:
        verbose_name = _('Group Email')
