from django.test import TestCase
import email_system.services.tq_email_templates as tmps


class TqTemplateTest(TestCase):
    def test_basic(self):
        context = {"course": "Ballroom 1"}
        subject, plaintext, html = tmps.PAYMENT_REMINDER.render(context)

        self.assertEqual(subject, "Payment Reminder Ballroom 1")
        self.assertIn(
            "We think that you did not yet pay the course fee for the course Ballroom 1.",
            plaintext,
        )
        self.assertIsNone(html)
