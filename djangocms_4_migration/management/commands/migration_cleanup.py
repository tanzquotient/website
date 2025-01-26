import logging

from cms.models import (
    Placeholder,
    Page,
    PageContent,
)
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db import connection, IntegrityError
from djangocms_versioning.models import Version

logger = logging.getLogger(__name__)


def _delete_page(page):
    try:
        logger.info("Deleting Page %s" % page.id)
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM cms_pageurl WHERE page_id = %s", [page.id])
            cursor.execute("DELETE FROM cms_page WHERE id = %s", [page.id])

    except IntegrityError as err:
        logger.error("Couldn't delete Page %s %s" % (page.id, err))


def _delete_page_content_placeholders(page_content_contenttype, page_content):
    placeholders = Placeholder.objects.filter(
        object_id=page_content.pk,
        content_type=page_content_contenttype,
    )
    for placeholder in placeholders:
        try:
            logger.debug("Deleting PageContent Placeholder %s" % placeholder.id)
            placeholder.delete()
        except IntegrityError as err:
            logger.error(
                "Couldn't delete PageContent Placeholder %s %s" % (placeholder.id, err)
            )


def _delete_page_content(page_content):
    try:
        logger.debug("Deleting PageContent %s" % page_content.id)
        page_content.delete()
    except IntegrityError as err:
        logger.error("Couldn't delete PageContent %s %s" % (page_content.id, err))


def _get_page_contents(page):
    return PageContent._base_manager.filter(page=page)


class Command(BaseCommand):
    help = "Run after migrations are applied"

    def handle(self, *args, **options):
        page_content_contenttype = ContentType.objects.get(
            app_label="cms", model="pagecontent"
        )
        page_list = Page.objects.all()

        stats = {
            "page_count": page_list.count(),
            "page_deleted": 0,
            "pagecontents_count": 0,
            "pagecontents_deleted": 0,
        }

        for page in page_list:
            page_content_list = _get_page_contents(page)

            if not page_content_list.exists():
                _delete_page(page)
                stats["page_deleted"] = stats["page_deleted"] + 1
                continue

            stats["pagecontents_count"] = (
                stats["pagecontents_count"] + page_content_list.count()
            )

            # Find if each PageContents has versions attached.
            for page_content in page_content_list:
                # If there are no versions for the pagecontents clean them out as they are not required
                if not Version.objects.filter(
                    object_id=page_content.pk,
                    content_type=page_content_contenttype,
                ).count():
                    _delete_page_content_placeholders(
                        page_content_contenttype, page_content
                    )
                    _delete_page_content(page_content)
                    stats["pagecontents_deleted"] = stats["pagecontents_deleted"] + 1

        logger.info("Stats: %s", str(stats))
