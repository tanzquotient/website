from django.db import models


class PageData(models.Model):
    title_id = models.CharField("title id", max_length=50)
    language = models.CharField("language", max_length=15)
    creation_date = models.DateTimeField("creation date", editable=False, blank=True, null=True)

    # Store the published state of a Page title
    published = models.BooleanField(blank=True)
    publisher_is_draft = models.BooleanField()
    # Ignored from Title: publisher_public
    publisher_state = models.SmallIntegerField()
    # This is the opposite and called publisher_public_id in CMS 3.5 which is confusing as a published page points at a draft
    opposite_number_id = models.CharField("publisher public id", max_length=20, blank=True, null=True)

    # page details
    page_id = models.CharField("page id", max_length=50)
    # This is the opposite and called publisher_public_id in CMS 3.5 which is confusing as a published page points at a draft
    page_opposite_number_id = models.CharField("publisher public id", max_length=20, blank=True, null=True)
    page_publisher_is_draft = models.BooleanField()
    path = models.CharField("path", max_length=255)