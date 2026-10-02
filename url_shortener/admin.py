from datetime import timedelta
from urllib.parse import parse_qsl, urlencode

from django import forms
from django.contrib import admin, messages
from django.contrib.admin.widgets import AdminDateWidget
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.shortcuts import render
from django.urls import path, reverse
from django.utils import timezone

from utils.export import export_csv

from .models import Destination, Source, Visit


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
    source = forms.ModelChoiceField(queryset=Source.objects.order_by("description"))
    destination = forms.ModelChoiceField(queryset=Destination.objects.order_by("url"))
    destination_parameters = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        help_text=(
            "Enter ordinary destination query parameters, for example "
            "campaign=autumn&f=partner-a. Their names are automatically prefixed "
            "with q_ in the generated URL."
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

        if request.method == "POST" and form.is_valid():
            parameters = [
                ("f", form.cleaned_data["source"].id),
                ("t", form.cleaned_data["destination"].id),
                *[
                    (f"q_{name}", value)
                    for name, value in form.cleaned_data["destination_parameters"]
                ],
            ]
            generated_url = request.build_absolute_uri(
                f"{reverse('url_shortener:redirect')}?{urlencode(parameters)}"
            )

        context = {
            **self.admin_site.each_context(request),
            "form": form,
            "generated_url": generated_url,
            "title": "Create shortened URL",
        }
        return render(
            request, "admin/url_shortener/source/create_shortened_url.html", context
        )


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ("id", "url")
    search_fields = ("url",)
    actions = ("export_visits_csv",)

    @admin.action(description="Download all visits to selected destination as CSV")
    def export_visits_csv(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(
                request,
                "Select exactly one destination to export its visits.",
                level=messages.ERROR,
            )
            return None

        destination = queryset.get()
        rows = [
            [
                "visit_id",
                "source_id",
                "source_description",
                "destination_id",
                "destination_url",
                "visited_at",
            ],
            *[
                [
                    visit.id,
                    visit.source_id,
                    visit.source.description,
                    destination.id,
                    destination.url,
                    visit.visited_at.isoformat(),
                ]
                for visit in Visit.objects.filter(destination=destination)
                .select_related("source")
                .order_by("visited_at", "id")
            ],
        ]
        return export_csv(f"visits-to-destination-{destination.id}", rows)


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ("id", "source", "destination", "visited_at")
    list_select_related = ("source", "destination")
    readonly_fields = ("visited_at",)
    change_list_template = "admin/url_shortener/visit/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        chart_urls = [
            path(
                "chart/",
                self.admin_site.admin_view(self.chart_view),
                name="url_shortener_visit_chart",
            ),
        ]
        return chart_urls + urls

    def chart_view(self, request):
        today = timezone.localdate()
        default_start = today - timedelta(days=29)
        form = VisitChartForm(request.GET or None)
        chart_data = None
        date_from = None
        date_to = None

        if form.is_valid():
            source = form.cleaned_data["source"]
            destination = form.cleaned_data["destination"]
            date_from = form.cleaned_data["date_from"] or default_start
            date_to = form.cleaned_data["date_to"] or today

            visits = Visit.objects.filter(
                destination=destination,
                visited_at__date__range=(date_from, date_to),
            )
            if source:
                visits = visits.filter(source=source)
                series = [
                    {
                        "id": source.id,
                        "name": source.description,
                        "color": "#417690",
                    }
                ]
            else:
                series = [
                    {
                        "id": entry["source_id"],
                        "name": entry["source__description"],
                        "color": f"hsl({index * 137 % 360} 55% 40%)",
                    }
                    for index, entry in enumerate(
                        visits.values("source_id", "source__description")
                        .distinct()
                        .order_by("source__description", "source_id")
                    )
                ]

            counts_by_day_and_source = {
                (entry["day"], entry["source_id"]): entry["count"]
                for entry in (
                    visits.annotate(day=TruncDate("visited_at"))
                    .values("day", "source_id")
                    .annotate(count=Count("id"))
                )
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
                ),
                default=1,
            )
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
                            "count": counts_by_day_and_source.get(
                                (day, item["id"]), 0
                            ),
                            "height": counts_by_day_and_source.get(
                                (day, item["id"]), 0
                            )
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
            "title": "Visits per day",
        }
        return render(request, "admin/url_shortener/visit/chart.html", context)
