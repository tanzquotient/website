from datetime import datetime

from post_office import mail

from courses.models import UserProfile
from email_system.models import GeneratedIndividualEmail
from tq_website import settings
from utils import TranslationUtils

def _get_language(user):
    try:
        return user.profile.language
    except UserProfile.DoesNotExist:
        return 'en'

def send_email(group_email):
    for user in group_email.target_group.user_set.all():

        # Get context for email
        context = {
            'first_name': user.first_name,
            'last_name': user.last_name,
        }

        group_email.set_current_language(_get_language(user))
        subject = TranslationUtils.get_text_with_language_fallback(group_email, 'subject')
        html_message = TranslationUtils.get_text_with_language_fallback(group_email, 'message')

        # Send email
        email = mail.send(
            recipients=[user.email],
            sender=settings.DEFAULT_FROM_EMAIL,
            subject=subject,
            html_message=html_message,
            context=context,
        )

        # Save generated mail
        GeneratedIndividualEmail.objects.create(email=email, source=group_email)

    group_email.sent_at = datetime.now()
    group_email.save()
