from datetime import timedelta

from django import forms
from django.contrib import admin, messages
from django.contrib.admin.widgets import AdminDateWidget
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.shortcuts import render
from django.urls import path
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


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ("id", "description")
    search_fields = ("description",)


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
