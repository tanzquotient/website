from datetime import datetime

from post_office import mail

from courses.models import UserProfile
from email_system.models import GeneratedIndividualEmail, TqEmailAddress
from tq_website import settings
from groups.definitions import GroupDefinitions
from ..models import UnsubscribeCode
from utils import TranslationUtils


def _get_language(user):
    try:
        return user.profile.language
    except UserProfile.DoesNotExist:
        return 'en'


def send_email(group_email):
    unsubscribe_context = None
    if group_email.target_group.name == GroupDefinitions.NEWSLETTER.name:
        unsubscribe_context = GroupDefinitions.NEWSLETTER.name
    elif group_email.target_group.name == GroupDefinitions.GET_INVOLVED.name:
        unsubscribe_context = GroupDefinitions.GET_INVOLVED.name
    elif group_email.target_group.name == GroupDefinitions.TEST.name:
        unsubscribe_context = GroupDefinitions.TEST.name

    for user in group_email.target_group.user_set.all():

        # Get context for email
        context = {
            'first_name': user.first_name,
            'last_name': user.last_name,
        }

        group_email.set_current_language(_get_language(user))
        subject = TranslationUtils.get_text_with_language_fallback(group_email, 'subject')
        html_message = TranslationUtils.get_text_with_language_fallback(group_email, 'message')

        headers = {}
        if group_email.reply_to is not None:
            headers['Reply-to'] = '<{}>'.format(group_email.reply_to.email_address)

        if unsubscribe_context is not None:
            unsubscribe_code, _ = UnsubscribeCode.objects.get_or_create(user=user)
            unsubscribe_url = unsubscribe_code.get_unsubscribe_url(unsubscribe_context)
            headers['List-unsubscribe'] = unsubscribe_url
            html_message += '<p><a href="{}">Unsubscribe here</a></p>'.format(unsubscribe_url)

        # Send email
        email = mail.send(
            recipients=[user.email],
            sender=settings.DEFAULT_FROM_EMAIL,
            subject=subject,
            headers=headers,
            html_message=html_message,
            context=context,
        )

        # Save generated mail
        GeneratedIndividualEmail.objects.create(email=email, source=group_email)

    group_email.sent_at = datetime.now()
    group_email.save()
