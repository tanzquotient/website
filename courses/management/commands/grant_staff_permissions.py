from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Grant staff permissions to a user specified by their email'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email of the user')

    def handle(self, *args, **options):
        email = options['email']
        User = get_user_model()

        try:
            user = User.objects.get(email=email)
            user.is_staff = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Staff permissions granted to user with email: {email}"))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"User with email {email} does not exist"))
