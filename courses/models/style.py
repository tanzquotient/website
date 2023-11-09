from typing import Iterable

from django.db import models
from django.db.models import SET_NULL
from djangocms_text_ckeditor.fields import HTMLField
from parler.models import TranslatableModel, TranslatedFields


class Style(TranslatableModel):
    name = models.CharField(max_length=30, unique=True, blank=False)
    parent_style = models.ForeignKey(
        to="Style", null=True, blank=True, related_name="children", on_delete=SET_NULL
    )
    filter_enabled = models.BooleanField(default=False, null=False, blank=False)
    filter_enabled.help_text = (
        "If set to true, users can filter courses list based on this style"
    )
    url_info = models.URLField(max_length=500, blank=True, null=True)
    url_info.help_text = "A url to an information page (e.g. Wikipedia)."
    url_video = models.URLField(max_length=500, blank=True, null=True)
    url_video.help_text = "A url to a demo video (e.g Youtube)."
    url_playlist = models.URLField(max_length=500, blank=True, null=True)
    url_playlist.help_text = "A url to a playlist (e.g on online-Spotify, Youtube)."

    translations = TranslatedFields(
        description=HTMLField(verbose_name="[TR] Description", blank=True, null=True)
    )

    def has_external_urls(self) -> bool:
        return (
            self.url_info is not None
            or self.url_video is not None
            or self.url_playlist is not None
        )

    def __str__(self) -> str:
        return "{}".format(self.name)

    class Meta:
        ordering = ["name"]

    def is_child_of(self, style: "Style") -> bool:
        current_style = self
        while current_style is not None:
            current_style = current_style.parent_style
            if current_style == style:
                return True

        return False

    def descendants(self) -> Iterable["Style"]:
        yield self
        for child in self.children.all():
            for descendant in child.descendants():
                yield descendant

    def ancestors(self) -> Iterable["Style"]:
        yield self
        if self.parent_style:
            for ancestor in self.parent_style.ancestors():
                yield ancestor

    def related(self) -> Iterable["Style"]:
        return set(self.descendants()).union(set(self.ancestors()))
