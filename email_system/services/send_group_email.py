from datetime import datetime

from courses.models import UserProfile
from email_system.models import GeneratedIndividualEmail, GroupEmail
from groups.definitions import GroupDefinitions
from utils import TranslationUtils
from . import send_all_emails
from ..models import UnsubscribeCode


def _get_language(user) -> str:
    try:
        return user.profile.language
    except UserProfile.DoesNotExist:
        return "en"


def send_group_email(group_email: GroupEmail) -> None:
    unsubscribe_context = None
    if group_email.target_group.name == GroupDefinitions.NEWSLETTER.name:
        unsubscribe_context = GroupDefinitions.NEWSLETTER.name
    elif group_email.target_group.name == GroupDefinitions.GET_INVOLVED.name:
        unsubscribe_context = GroupDefinitions.GET_INVOLVED.name
    elif group_email.target_group.name == GroupDefinitions.TEST.name:
        unsubscribe_context = GroupDefinitions.TEST.name

    BATCH_SIZE = 100
    target_users = list(group_email.target_group.user_set.all())
    target_users_batches = [target_users[i:i + BATCH_SIZE] for i in range(0, len(target_users), BATCH_SIZE)]
    
    for batch in target_users_batches:
        emails = []

        for user in batch:
            # Get context for email
            context = {
                "first_name": user.first_name,
                "last_name": user.last_name,
            }

            group_email.set_current_language(_get_language(user))
            subject = TranslationUtils.get_text_with_language_fallback(
                group_email, "subject"
            )
            html_message = TranslationUtils.get_text_with_language_fallback(
                group_email, "message"
            )

            headers = {}
            if group_email.reply_to is not None:
                headers["Reply-to"] = group_email.reply_to.email_address

            if unsubscribe_context is not None:
                unsubscribe_code, _ = UnsubscribeCode.objects.get_or_create(user=user)
                unsubscribe_url = unsubscribe_code.get_unsubscribe_url(unsubscribe_context)
                headers["List-unsubscribe"] = "<{}>".format(unsubscribe_url)
                html_message += '<p><a href="{}">Unsubscribe here</a></p>'.format(
                    unsubscribe_url
                )

            # Add email
            emails.append(
                dict(
                    to=user.email,
                    subject=subject,
                    headers=headers,
                    html_message=html_message,
                    context=context,
                )
            )

        sent_emails = send_all_emails(emails)
        for email in sent_emails:
            # Save generated mail
            GeneratedIndividualEmail.objects.create(email=email, source=group_email)

    group_email.sent_at = datetime.now()
    group_email.save()