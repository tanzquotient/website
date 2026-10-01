from django.contrib import admin

from .models import Destination, Source, Visit


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ("id", "description")
    search_fields = ("description",)


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ("id", "url")
    search_fields = ("url",)


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ("id", "source", "destination", "visited_at")
    list_select_related = ("source", "destination")
    readonly_fields = ("visited_at",)
