from email_system.models import GroupEmail
from tq_website import settings


def copy_group_email(group_email) -> None:
    old_id = group_email.id
    group_email.id = None
    group_email.sent_at = None
    group_email.save()
    old = GroupEmail.objects.get(id=old_id)

    for language_code, _ in settings.LANGUAGES:
        group_email.set_current_language(language_code)
        old.set_current_language(language_code)
        group_email.subject = old.subject
        group_email.message = old.message

    group_email.save()
