from django.db.models.signals import post_save
from django.dispatch import receiver
import auditing.models as my_models
from django.core.mail import send_mail
from django.conf import settings
from tq_website import settings as my_settings


@receiver(post_save, sender=my_models.Problem)
def problem_add_handler(sender, **kwargs):
    problem = kwargs.get('instance')

    send_mail(u'Problem occurred in TQ System',
              u'A problem occurred in TQ System. Please check what the problem was, in Admin area -> Audit section -> Problem.\n\nTag: {}\nMessage:\n{}\n'.format(
                  problem.tag, problem.message), my_settings.EMAIL_HOST_USER,
              [my_settings.EMAIL_HOST_USER], fail_silently=True)
