from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Destination, Source, Visit


class RedirectToDestinationTests(TestCase):
    def setUp(self):
        self.source = Source.objects.create(description="Newsletter")
        self.destination = Destination.objects.create(url="https://example.com/event")

    def test_valid_ids_create_a_visit_and_redirect_without_a_body(self):
        response = self.client.get(
            reverse("url_shortener:redirect"),
            {"f": self.source.id, "t": self.destination.id},
            REMOTE_ADDR="203.0.113.10",
            HTTP_USER_AGENT="Example browser",
        )

        self.assertRedirects(
            response, self.destination.url, fetch_redirect_response=False
        )
        self.assertEqual(response.content, b"")
        visit = Visit.objects.get(source=self.source, destination=self.destination)
        self.assertEqual(visit.ip_address, "203.0.113.10")
        self.assertEqual(visit.user_agent, "Example browser")

    def test_invalid_ids_return_a_generic_error_without_creating_a_visit(self):
        for parameters in (
            {"f": 9999, "t": self.destination.id},
            {"f": self.source.id, "t": 9999},
            {"t": self.destination.id},
        ):
            response = self.client.get(reverse("url_shortener:redirect"), parameters)

            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.content, b"Ooops, something went wrong...")

        self.assertFalse(Visit.objects.exists())

    def test_duplicate_tracking_ids_return_a_generic_error(self):
        response = self.client.get(
            f"{reverse('url_shortener:redirect')}?f={self.source.id}&f=9999&"
            f"t={self.destination.id}"
        )

        self.assertEqual(response.status_code, 404)
        self.assertFalse(Visit.objects.exists())

    def test_forwarded_parameters_are_added_to_the_destination_url(self):
        response = self.client.get(
            reverse("url_shortener:redirect"),
            {
                "f": self.source.id,
                "t": self.destination.id,
                "q_campaign": "autumn",
                "q_f": "partner-a",
            },
        )

        self.assertRedirects(
            response,
            "https://example.com/event?campaign=autumn&f=partner-a",
            fetch_redirect_response=False,
        )

    def test_forwarded_parameters_override_destination_parameters(self):
        self.destination.url = "https://example.com/event?campaign=old&keep=yes"
        self.destination.save()

        response = self.client.get(
            reverse("url_shortener:redirect"),
            {
                "f": self.source.id,
                "t": self.destination.id,
                "q_campaign": "new",
            },
        )

        self.assertRedirects(
            response,
            "https://example.com/event?keep=yes&campaign=new",
            fetch_redirect_response=False,
        )


class CreateShortenedUrlAdminTests(TestCase):
    def setUp(self):
        self.source = Source.objects.create(description="Newsletter")
        self.destination = Destination.objects.create(url="https://example.com/event")
        self.user = get_user_model().objects.create_superuser(
            username="url-shortener-admin",
            email="admin@example.com",
            password="password",
        )
        self.client.force_login(self.user)
        self.url = reverse("admin:url_shortener_create_shortened_url")

    def test_admin_can_generate_a_url_with_prefixed_destination_parameters(self):
        response = self.client.post(
            self.url,
            {
                "source": self.source.id,
                "destination": self.destination.id,
                "destination_parameters": "campaign=autumn&f=partner-a",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["generated_url"],
            "http://testserver/url_shortener/"
            f"?f={self.source.id}&t={self.destination.id}"
            "&q_campaign=autumn&q_f=partner-a",
        )
        self.assertFalse(Visit.objects.exists())

    def test_admin_rejects_malformed_destination_parameters(self):
        response = self.client.post(
            self.url,
            {
                "source": self.source.id,
                "destination": self.destination.id,
                "destination_parameters": "not-a-parameter",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enter parameters in the form name=value.")
        self.assertIsNone(response.context["generated_url"])
