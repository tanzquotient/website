from django.test import TestCase
from django.contrib.auth import get_user_model
from io import StringIO
from django.core.management import call_command
import re


class GrantUserPermissionsTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )

    def strip_ansi_escape_sequences(self, text):
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)

    def test_grant_superuser_permission(self):
        out = StringIO()
        email = 'testuser@example.com'

        call_command('grant_superuser_permissions', email, stdout=out)

        user = self.User.objects.get(email=email)

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        expected_output = f"Superuser permissions granted to user with email: {email}"
        self.assertEqual(self.strip_ansi_escape_sequences(out.getvalue().strip()), expected_output)

    def test_grant_superuser_permission_nonexistent_user(self):
        out = StringIO()
        email = 'nonexistentuser@example.com'

        call_command('grant_superuser_permissions', email, stdout=out)

        user_exists = self.User.objects.filter(email=email).exists()

        self.assertFalse(user_exists)
        expected_output = f"User with email {email} does not exist"
        self.assertEqual(self.strip_ansi_escape_sequences(out.getvalue().strip()), expected_output)

    def test_grant_staff_permission(self):
        out = StringIO()
        email = 'testuser@example.com'

        call_command('grant_staff_permissions', email, stdout=out)

        user = self.User.objects.get(email=email)

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_staff)
        expected_output = f"Staff permissions granted to user with email: {email}"
        self.assertEqual(self.strip_ansi_escape_sequences(out.getvalue().strip()), expected_output)

    def test_grant_staff_permission_nonexistent_user(self):
        out = StringIO()
        email = 'nonexistentuser@example.com'

        call_command('grant_staff_permissions', email, stdout=out)

        user_exists = self.User.objects.filter(email=email).exists()

        self.assertFalse(user_exists)
        expected_output = f"User with email {email} does not exist"
        self.assertEqual(self.strip_ansi_escape_sequences(out.getvalue().strip()), expected_output)


