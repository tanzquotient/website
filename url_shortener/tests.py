from datetime import datetime, time, timedelta

from django.conf import settings
from django.contrib import admin
from django.contrib.auth import (
    BACKEND_SESSION_KEY,
    HASH_SESSION_KEY,
    SESSION_KEY,
    get_user_model,
)
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Destination, ShortLink, Source, Visit


def authenticate_test_client(client, user):
    session = client.session
    session[SESSION_KEY] = str(user.pk)
    session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
    session[HASH_SESSION_KEY] = user.get_session_auth_hash()
    session.save()


def create_visit_on(short_link, day):
    visit = Visit.objects.create(short_link=short_link)
    visited_at = timezone.make_aware(datetime.combine(day, time.min))
    Visit.objects.filter(pk=visit.pk).update(visited_at=visited_at)


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
        )

        self.assertRedirects(
            response,
            "https://example.com/event?f=external-source&t=external-destination",
            fetch_redirect_response=False,
        )
        self.assertEqual(response.content, b"")
        visit = Visit.objects.get(short_link=self.short_link)
        self.assertEqual(visit.short_link, self.short_link)

    def test_valid_link_stores_the_authenticated_user(self):
        user = get_user_model().objects.create_user(
            username="short-link-visitor",
            email="short-link-visitor@example.com",
            password="password",
        )
        authenticate_test_client(self.client, user)

        self.client.get(self.url)

        self.assertEqual(Visit.objects.get(short_link=self.short_link).user, user)

    def test_unknown_or_unavailable_link_returns_a_generic_error_without_a_visit(self):
        response = self.client.get(
            reverse("url_shortener:redirect", kwargs={"tag": "unknown-link"})
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content, b"Ooops, something went wrong...")
        self.assertFalse(Visit.objects.exists())

        self.short_link.deactivated = True
        self.short_link.save()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content, b"Ooops, something went wrong...")
        self.assertFalse(Visit.objects.exists())

    def test_link_outside_its_validity_window_returns_a_generic_error(self):
        self.short_link.valid_from = timezone.now() + timedelta(days=1)
        self.short_link.save()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(Visit.objects.exists())

        self.short_link.valid_from = None
        self.short_link.valid_until = timezone.now() - timedelta(days=1)
        self.short_link.save()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(Visit.objects.exists())

    def test_link_inside_its_validity_window_redirects_and_creates_a_visit(self):
        now = timezone.now()
        self.short_link.valid_from = now - timedelta(minutes=1)
        self.short_link.valid_until = now + timedelta(minutes=1)
        self.short_link.save()

        response = self.client.get(self.url)

        self.assertRedirects(
            response,
            self.destination.url,
            fetch_redirect_response=False,
        )
        self.assertTrue(Visit.objects.filter(short_link=self.short_link).exists())

    def test_redirect_endpoint_only_accepts_get_requests(self):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 405)
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
        authenticate_test_client(self.client, self.user)
        self.url = reverse("admin:url_shortener_create_shortened_url")

    def test_admin_creates_a_short_link_with_unprefixed_destination_parameters(self):
        response = self.client.post(
            self.url,
            {
                "description": "Autumn newsletter",
                "source": self.source.id,
                "destination": self.destination.id,
                "destination_parameters": "campaign=autumn&f=partner-a",
            },
        )

        self.assertEqual(response.status_code, 200)
        short_link = ShortLink.objects.get()
        self.assertEqual(len(short_link.tag), 16)
        self.assertEqual(short_link.description, "Autumn newsletter")
        self.assertEqual(short_link.source, self.source)
        self.assertEqual(short_link.destination, self.destination)
        self.assertEqual(
            response.context["generated_url"],
            f"http://testserver/de/shorty/{short_link.tag}/?campaign=autumn&f=partner-a",
        )
        self.assertTrue(
            response.context["qr_code_data"].startswith("data:image/svg+xml;base64,")
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

    def test_short_link_change_page_shows_the_url_and_qr_code(self):
        short_link = ShortLink.objects.create(
            source=self.source, destination=self.destination
        )

        response = self.client.get(
            reverse("admin:url_shortener_shortlink_change", args=[short_link.id])
        )

        self.assertContains(response, f"http://testserver/de/shorty/{short_link.tag}/")
        self.assertContains(response, "QR code for this short URL")
        self.assertTrue(
            response.context["qr_code_data"].startswith("data:image/svg+xml;base64,")
        )

    def test_short_link_routing_fields_are_read_only_after_a_visit(self):
        short_link = ShortLink.objects.create(
            source=self.source, destination=self.destination
        )
        Visit.objects.create(short_link=short_link)
        short_link_admin = admin.site._registry[ShortLink]

        readonly_fields = short_link_admin.get_readonly_fields(None, short_link)

        self.assertIn("source", readonly_fields)
        self.assertIn("destination", readonly_fields)

    def test_visit_exports_include_the_expected_visits(self):
        short_link = ShortLink.objects.create(
            source=self.source, destination=self.destination
        )
        Visit.objects.create(short_link=short_link)

        response = self.client.get(reverse("admin:url_shortener_visit_export"))
        self.assertContains(response, "visit_id")
        self.assertContains(response, short_link.tag)

        response = self.client.get(
            reverse("admin:url_shortener_visit_chart_export"),
            {"destination": self.destination.id},
        )
        self.assertContains(response, "visit_id")
        self.assertContains(response, short_link.tag)

    def test_chart_export_only_contains_the_selected_source_and_destination(self):
        selected_link = ShortLink.objects.create(
            source=self.source, destination=self.destination
        )
        other_source = Source.objects.create(description="Social media")
        other_source_link = ShortLink.objects.create(
            source=other_source, destination=self.destination
        )
        other_destination_link = ShortLink.objects.create(
            source=self.source,
            destination=Destination.objects.create(url="https://example.com/other"),
        )
        Visit.objects.create(short_link=selected_link)
        Visit.objects.create(short_link=other_source_link)
        Visit.objects.create(short_link=other_destination_link)

        response = self.client.get(
            reverse("admin:url_shortener_visit_chart_export"),
            {
                "source": self.source.id,
                "destination": self.destination.id,
                "date_from": timezone.localdate().isoformat(),
                "date_to": timezone.localdate().isoformat(),
            },
        )

        self.assertContains(response, selected_link.tag)
        self.assertNotContains(response, other_source_link.tag)
        self.assertNotContains(response, other_destination_link.tag)

    def test_chart_export_rejects_missing_or_invalid_chart_selection(self):
        response = self.client.get(reverse("admin:url_shortener_visit_chart_export"))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content,
            b"Choose a valid chart before exporting it.",
        )

    def test_chart_includes_zero_days_and_stacks_sources(self):
        second_source = Source.objects.create(description="Social media")
        first_link = ShortLink.objects.create(
            source=self.source, destination=self.destination
        )
        second_link = ShortLink.objects.create(
            source=second_source, destination=self.destination
        )
        today = timezone.localdate()
        create_visit_on(first_link, today - timedelta(days=2))
        create_visit_on(first_link, today)
        create_visit_on(second_link, today)

        response = self.client.get(
            reverse("admin:url_shortener_visit_chart"),
            {
                "destination": self.destination.id,
                "date_from": (today - timedelta(days=2)).isoformat(),
                "date_to": today.isoformat(),
            },
        )

        chart_data = response.context["chart_data"]
        self.assertEqual([item["count"] for item in chart_data], [1, 0, 2])
        self.assertEqual(len(chart_data[-1]["segments"]), 2)
        self.assertContains(response, "Download displayed visits as CSV")

    def test_destination_csv_action_exports_one_destination_and_rejects_multiple(self):
        short_link = ShortLink.objects.create(
            source=self.source, destination=self.destination
        )
        Visit.objects.create(short_link=short_link)
        changelist_url = reverse("admin:url_shortener_destination_changelist")

        response = self.client.post(
            changelist_url,
            {
                "action": "export_visits_csv",
                "_selected_action": [self.destination.id],
            },
        )

        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertContains(response, short_link.tag)

        other_destination = Destination.objects.create(url="https://example.com/other")
        response = self.client.post(
            changelist_url,
            {
                "action": "export_visits_csv",
                "_selected_action": [self.destination.id, other_destination.id],
            },
            follow=True,
        )

        self.assertContains(
            response,
            "Select exactly one destination to export its visits.",
        )

    def test_destination_change_page_links_to_its_chart(self):
        response = self.client.get(
            reverse(
                "admin:url_shortener_destination_change", args=[self.destination.id]
            )
        )

        self.assertContains(response, "View visits per day chart for this destination")
        self.assertContains(
            response,
            f"destination={self.destination.id}",
            html=False,
        )

    def test_dashboard_shows_visit_totals_and_rankings(self):
        short_link = ShortLink.objects.create(
            source=self.source, destination=self.destination
        )
        Visit.objects.create(short_link=short_link)

        response = self.client.get(reverse("admin:url_shortener_visit_dashboard"))

        self.assertContains(response, "Visit totals")
        self.assertContains(response, "Last 30 days")
        self.assertContains(response, self.source.description)
        self.assertContains(response, self.destination.url)
        self.assertContains(response, "View chart")

    def test_dashboard_uses_30_day_window_and_orders_rankings_by_visits(self):
        second_source = Source.objects.create(description="Social media")
        first_link = ShortLink.objects.create(
            source=self.source, destination=self.destination
        )
        second_link = ShortLink.objects.create(
            source=second_source, destination=self.destination
        )
        today = timezone.localdate()
        create_visit_on(first_link, today)
        create_visit_on(second_link, today)
        create_visit_on(second_link, today)
        create_visit_on(second_link, today - timedelta(days=30))

        response = self.client.get(reverse("admin:url_shortener_visit_dashboard"))

        self.assertEqual(response.context["today_visits"], 3)
        self.assertEqual(response.context["last_7_days_visits"], 3)
        self.assertEqual(response.context["last_30_days_visits"], 3)
        self.assertEqual(
            response.context["top_sources"][0]["short_link__source__description"],
            second_source.description,
        )

    def test_url_shortener_admin_index_redirects_to_the_dashboard(self):
        response = self.client.get(
            reverse("admin:app_list", kwargs={"app_label": "url_shortener"})
        )

        self.assertRedirects(
            response,
            reverse("admin:url_shortener_visit_dashboard"),
            fetch_redirect_response=False,
        )

    def test_url_shortener_admin_views_require_login(self):
        self.client.logout()

        response = self.client.get(reverse("admin:url_shortener_visit_dashboard"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)
