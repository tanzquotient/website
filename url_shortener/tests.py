from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Destination, ShortLink, Source, Visit


class RedirectToDestinationTests(TestCase):
    def setUp(self):
        self.source = Source.objects.create(description="Newsletter")
        self.destination = Destination.objects.create(url="https://example.com/event")
        self.short_link = ShortLink.objects.create(
            source=self.source, destination=self.destination
        )
        self.url = reverse(
            "url_shortener:redirect", kwargs={"tag": self.short_link.tag}
        )

    def test_valid_link_creates_a_visit_and_redirects_without_a_body(self):
        response = self.client.get(
            self.url,
            {"f": "external-source", "t": "external-destination"},
            REMOTE_ADDR="203.0.113.10",
            HTTP_USER_AGENT="Example browser",
        )

        self.assertRedirects(
            response,
            "https://example.com/event?f=external-source&t=external-destination",
            fetch_redirect_response=False,
        )
        self.assertEqual(response.content, b"")
        visit = Visit.objects.get(short_link=self.short_link)
        self.assertEqual(visit.short_link, self.short_link)
        self.assertEqual(visit.ip_address, "203.0.113.10")
        self.assertEqual(visit.user_agent, "Example browser")

    def test_unknown_or_inactive_link_returns_a_generic_error_without_a_visit(self):
        response = self.client.get(
            reverse("url_shortener:redirect", kwargs={"tag": "unknown-link"})
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content, b"Ooops, something went wrong...")
        self.assertFalse(Visit.objects.exists())

        self.short_link.active = False
        self.short_link.save()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content, b"Ooops, something went wrong...")
        self.assertFalse(Visit.objects.exists())

    def test_request_parameters_are_forwarded_without_prefixes(self):
        response = self.client.get(
            self.url,
            {
                "campaign": "autumn",
                "f": "partner-a",
                "tag": ["first", "second"],
            },
        )

        self.assertRedirects(
            response,
            "https://example.com/event?campaign=autumn&f=partner-a&tag=first&tag=second",
            fetch_redirect_response=False,
        )

    def test_request_parameters_are_appended_to_destination_parameters(self):
        self.destination.url = "https://example.com/event?campaign=old&keep=yes"
        self.destination.save()

        response = self.client.get(
            self.url,
            {
                "campaign": "new",
            },
        )

        self.assertRedirects(
            response,
            "https://example.com/event?campaign=old&keep=yes&campaign=new",
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

    def test_admin_creates_a_short_link_with_unprefixed_destination_parameters(self):
        response = self.client.post(
            self.url,
            {
                "source": self.source.id,
                "destination": self.destination.id,
                "destination_parameters": "campaign=autumn&f=partner-a",
            },
        )

        self.assertEqual(response.status_code, 200)
        short_link = ShortLink.objects.get()
        self.assertEqual(len(short_link.tag), 16)
        self.assertEqual(short_link.source, self.source)
        self.assertEqual(short_link.destination, self.destination)
        self.assertEqual(
            response.context["generated_url"],
            f"http://testserver/url_shortener/{short_link.tag}/"
            "?campaign=autumn&f=partner-a",
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
        self.assertFalse(ShortLink.objects.exists())
