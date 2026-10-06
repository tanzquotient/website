import base64
from datetime import datetime, time, timedelta
from io import BytesIO
from urllib.parse import parse_qsl, urlencode

import qrcode
from django import forms
from django.contrib import admin, messages
from django.contrib.admin.widgets import AdminDateWidget
from django.core.exceptions import ValidationError
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.urls import path, reverse
from django.utils import timezone
from qrcode.image.svg import SvgPathImage

from utils.export import export_csv

from .models import Destination, ShortLink, Source, Visit


def qr_code_data_uri(value):
    image = qrcode.make(value, image_factory=SvgPathImage)
    buffer = BytesIO()
    image.save(buffer)
    encoded_svg = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded_svg}"


def visit_csv_rows(visits):
    return [
        [
            "visit_id",
            "source_id",
            "source_description",
            "destination_id",
            "destination_url",
            "short_link_tag",
            "visited_at",
        ],
        *[
            [
                visit.id,
                visit.short_link.source_id,
                visit.short_link.source.description,
                visit.short_link.destination_id,
                visit.short_link.destination.url,
                visit.short_link.tag,
                visit.visited_at.isoformat(),
            ]
            for visit in visits.select_related(
                "short_link__source",
                "short_link__destination",
            ).order_by("visited_at", "id")
        ],
    ]


def visit_date_range(date_from, date_to):
    timezone_info = timezone.get_current_timezone()
    return {
        "visited_at__gte": timezone.make_aware(
            datetime.combine(date_from, time.min), timezone_info
        ),
        "visited_at__lt": timezone.make_aware(
            datetime.combine(date_to + timedelta(days=1), time.min), timezone_info
        ),
    }


class VisitChartForm(forms.Form):
    source = forms.ModelChoiceField(
        queryset=Source.objects.order_by("description"),
        required=False,
        help_text="Leave blank to show all sources as a stacked chart.",
    )
    destination = forms.ModelChoiceField(queryset=Destination.objects.order_by("url"))
    date_from = forms.DateField(required=False, widget=AdminDateWidget)
    date_to = forms.DateField(required=False, widget=AdminDateWidget)

    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get("date_from")
        date_to = cleaned_data.get("date_to")

        if date_from and date_to and date_from > date_to:
            raise ValidationError("The start date must not be after the end date.")

        return cleaned_data


class ShortenedUrlForm(forms.Form):
    description = forms.CharField(
        required=False,
        help_text="Optional label to help identify this short URL in the admin.",
    )
    source = forms.ModelChoiceField(queryset=Source.objects.order_by("description"))
    destination = forms.ModelChoiceField(queryset=Destination.objects.order_by("url"))
    destination_parameters = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        help_text=(
            "Enter ordinary destination query parameters, for example "
            "campaign=autumn&f=partner-a. They are passed on unchanged."
        ),
    )

    def clean_destination_parameters(self):
        value = self.cleaned_data["destination_parameters"]
        try:
            parameters = parse_qsl(
                value, keep_blank_values=True, strict_parsing=bool(value)
            )
        except ValueError as error:
            raise ValidationError("Enter parameters in the form name=value.") from error

        if any(not name for name, _ in parameters):
            raise ValidationError("Destination parameter names must not be empty.")

        return parameters


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ("id", "description")
    search_fields = ("description",)
    change_list_template = "admin/url_shortener/source/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        create_url = [
            path(
                "create-shortened-url/",
                self.admin_site.admin_view(self.create_shortened_url_view),
                name="url_shortener_create_shortened_url",
            ),
        ]
        return create_url + urls

    def create_shortened_url_view(self, request):
        form = ShortenedUrlForm(request.POST or None)
        generated_url = None
        qr_code_data = None

        if request.method == "POST" and form.is_valid():
            short_link = ShortLink.objects.create(
                description=form.cleaned_data["description"],
                source=form.cleaned_data["source"],
                destination=form.cleaned_data["destination"],
            )
            generated_url = request.build_absolute_uri(
                reverse("url_shortener:redirect", kwargs={"tag": short_link.tag})
                + (
                    f"?{urlencode(form.cleaned_data['destination_parameters'])}"
                    if form.cleaned_data["destination_parameters"]
                    else ""
                )
            )
            qr_code_data = qr_code_data_uri(generated_url)

        context = {
            **self.admin_site.each_context(request),
            "form": form,
            "generated_url": generated_url,
            "qr_code_data": qr_code_data,
            "title": "Create shortened URL",
        }
        return render(
            request, "admin/url_shortener/source/create_shortened_url.html", context
        )


@admin.register(ShortLink)
class ShortLinkAdmin(admin.ModelAdmin):
    list_display = (
        "tag",
        "description",
        "source",
        "destination",
        "deactivated",
        "created_at",
    )
    list_select_related = ("source", "destination")
    list_filter = ("deactivated",)
    search_fields = ("tag", "description", "source__description", "destination__url")
    readonly_fields = ("tag", "created_at")
    change_form_template = "admin/url_shortener/shortlink/change_form.html"
    fieldsets = (
        ("Short URL", {"fields": ("tag", "description")}),
        ("Routing", {"fields": ("source", "destination")}),
        (
            "Availability",
            {"fields": ("deactivated", "valid_from", "valid_until", "created_at")},
        ),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.visits.exists():
            return (*self.readonly_fields, "source", "destination")
        return self.readonly_fields

    def change_view(self, request, object_id, form_url="", extra_context=None):
        short_link = self.get_object(request, object_id)
        if short_link is None:
            return super().change_view(request, object_id, form_url, extra_context)

        short_url = request.build_absolute_uri(
            reverse("url_shortener:redirect", kwargs={"tag": short_link.tag})
        )
        extra_context = {
            **(extra_context or {}),
            "short_url": short_url,
            "qr_code_data": qr_code_data_uri(short_url),
            "visits_url": (
                reverse("admin:url_shortener_visit_changelist")
                + f"?{urlencode({'short_link__id__exact': short_link.id})}"
            ),
            "chart_url": (
                reverse("admin:url_shortener_visit_chart")
                + f"?{urlencode({'destination': short_link.destination_id})}"
            ),
        }
        return super().change_view(request, object_id, form_url, extra_context)


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ("id", "url")
    search_fields = ("url",)
    actions = ("export_visits_csv",)
    change_form_template = "admin/url_shortener/destination/change_form.html"

    def change_view(self, request, object_id, form_url="", extra_context=None):
        destination = self.get_object(request, object_id)
        if destination is None:
            return super().change_view(request, object_id, form_url, extra_context)

        extra_context = {
            **(extra_context or {}),
            "chart_url": (
                reverse("admin:url_shortener_visit_chart")
                + f"?{urlencode({'destination': destination.id})}"
            ),
        }
        return super().change_view(request, object_id, form_url, extra_context)

    @admin.action(description="Download all visits to selected destination as CSV")
    def export_visits_csv(self, request, queryset):
        destinations = list(queryset[:2])
        if len(destinations) != 1:
            self.message_user(
                request,
                "Select exactly one destination to export its visits.",
                level=messages.ERROR,
            )
            return None

        destination = destinations[0]
        rows = visit_csv_rows(Visit.objects.filter(short_link__destination=destination))
        return export_csv(f"visits-to-destination-{destination.id}", rows)


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "short_link",
        "source",
        "destination",
        "visited_at",
    )
    list_select_related = ("short_link__source", "short_link__destination")
    readonly_fields = ("short_link", "visited_at")
    change_list_template = "admin/url_shortener/visit/change_list.html"

    @admin.display(ordering="short_link__source", description="Source")
    def source(self, obj):
        return obj.short_link.source

    @admin.display(ordering="short_link__destination", description="Destination")
    def destination(self, obj):
        return obj.short_link.destination

    def get_urls(self):
        urls = super().get_urls()
        report_urls = [
            path(
                "dashboard/",
                self.admin_site.admin_view(self.dashboard_view),
                name="url_shortener_visit_dashboard",
            ),
            path(
                "export/",
                self.admin_site.admin_view(self.export_all_visits_view),
                name="url_shortener_visit_export",
            ),
            path(
                "chart/export/",
                self.admin_site.admin_view(self.chart_export_view),
                name="url_shortener_visit_chart_export",
            ),
            path(
                "chart/",
                self.admin_site.admin_view(self.chart_view),
                name="url_shortener_visit_chart",
            ),
        ]
        return report_urls + urls

    def dashboard_view(self, request):
        today = timezone.localdate()
        last_7_days_start = today - timedelta(days=6)
        last_30_days_start = today - timedelta(days=29)
        today_start = visit_date_range(today, today)["visited_at__gte"]
        last_7_days_start_at = visit_date_range(last_7_days_start, today)[
            "visited_at__gte"
        ]
        last_30_days_start_at = visit_date_range(last_30_days_start, today)[
            "visited_at__gte"
        ]
        visit_totals = Visit.objects.aggregate(
            today_visits=Count("id", filter=Q(visited_at__gte=today_start)),
            last_7_days_visits=Count(
                "id", filter=Q(visited_at__gte=last_7_days_start_at)
            ),
            last_30_days_visits=Count(
                "id", filter=Q(visited_at__gte=last_30_days_start_at)
            ),
        )
        last_30_days_visits = Visit.objects.filter(
            visited_at__gte=last_30_days_start_at
        )
        top_destinations = list(
            last_30_days_visits.values(
                "short_link__destination_id", "short_link__destination__url"
            )
            .annotate(visits=Count("id"))
            .order_by("-visits", "short_link__destination__url")[:5]
        )
        for destination in top_destinations:
            destination["chart_url"] = (
                reverse("admin:url_shortener_visit_chart")
                + "?"
                + urlencode({"destination": destination["short_link__destination_id"]})
            )

        context = {
            **self.admin_site.each_context(request),
            "title": "URL shortener dashboard",
            **visit_totals,
            "top_sources": (
                last_30_days_visits.values(
                    "short_link__source_id", "short_link__source__description"
                )
                .annotate(visits=Count("id"))
                .order_by("-visits", "short_link__source__description")[:5]
            ),
            "top_destinations": top_destinations,
        }
        return render(request, "admin/url_shortener/visit/dashboard.html", context)

    def export_all_visits_view(self, request):
        return export_csv("all-visits", visit_csv_rows(Visit.objects.all()))

    def chart_selection(self, form):
        today = timezone.localdate()
        date_from = form.cleaned_data["date_from"] or today - timedelta(days=29)
        date_to = form.cleaned_data["date_to"] or today
        source = form.cleaned_data["source"]
        destination = form.cleaned_data["destination"]
        visits = Visit.objects.filter(
            short_link__destination=destination,
            **visit_date_range(date_from, date_to),
        )
        if source:
            visits = visits.filter(short_link__source=source)
        return source, destination, date_from, date_to, visits

    def chart_export_view(self, request):
        form = VisitChartForm(request.GET)
        if not form.is_valid():
            return HttpResponseBadRequest("Choose a valid chart before exporting it.")

        _, destination, date_from, date_to, visits = self.chart_selection(form)
        return export_csv(
            f"visits-to-destination-{destination.id}-{date_from}-to-{date_to}",
            visit_csv_rows(visits),
        )

    def chart_view(self, request):
        form = VisitChartForm(request.GET or None)
        chart_data = None
        date_from = None
        date_to = None

        if form.is_valid():
            source, destination, date_from, date_to, visits = self.chart_selection(form)
            if source:
                series = [
                    {
                        "id": source.id,
                        "name": source.description,
                        "color": "#417690",
                    }
                ]
            else:
                series = []

            count_entries = list(
                visits.annotate(day=TruncDate("visited_at"))
                .values(
                    "day",
                    "short_link__source_id",
                    "short_link__source__description",
                )
                .annotate(count=Count("id"))
            )
            if not source:
                source_entries = sorted(
                    {
                        (
                            entry["short_link__source_id"],
                            entry["short_link__source__description"],
                        )
                        for entry in count_entries
                    },
                    key=lambda entry: (entry[1], entry[0]),
                )
                series = [
                    {
                        "id": source_id,
                        "name": source_description,
                        "color": f"hsl({index * 137 % 360} 55% 40%)",
                    }
                    for index, (source_id, source_description) in enumerate(
                        source_entries
                    )
                ]

            counts_by_day_and_source = {
                (entry["day"], entry["short_link__source_id"]): entry["count"]
                for entry in count_entries
            }
            days = [
                date_from + timedelta(days=offset)
                for offset in range((date_to - date_from).days + 1)
            ]
            max_count = max(
                (
                    sum(
                        counts_by_day_and_source.get((day, item["id"]), 0)
                        for item in series
                    )
                    for day in days
                )
            )
            max_count = max(1, max_count)
            chart_data = [
                {
                    "date": day,
                    "count": sum(
                        counts_by_day_and_source.get((day, item["id"]), 0)
                        for item in series
                    ),
                    "segments": [
                        {
                            **item,
                            "count": counts_by_day_and_source.get((day, item["id"]), 0),
                            "height": counts_by_day_and_source.get((day, item["id"]), 0)
                            / max_count
                            * 100,
                        }
                        for item in series
                    ],
                }
                for day in days
            ]

        context = {
            **self.admin_site.each_context(request),
            "form": form,
            "chart_data": chart_data,
            "date_from": date_from,
            "date_to": date_to,
            "destination": form.cleaned_data["destination"]
            if chart_data is not None
            else None,
            "series": series if chart_data is not None else (),
            "csv_export_url": (
                reverse("admin:url_shortener_visit_chart_export")
                + "?"
                + urlencode(
                    {
                        "source": source.id if source else "",
                        "destination": destination.id,
                        "date_from": date_from.isoformat(),
                        "date_to": date_to.isoformat(),
                    }
                )
                if chart_data is not None
                else None
            ),
            "title": "Visits per day",
        }
        return render(request, "admin/url_shortener/visit/chart.html", context)
