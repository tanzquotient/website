import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site

logger = logging.getLogger(__name__)


def get_or_create_migration_user(user_model=get_user_model()):
    """
    :return: Object: User, Bool: if the user was created

    This is the user that is used to automatically attach to new items created as
    part of the cms migration.
    """
    return user_model.objects.get_or_create(
        username="djangocms_4_migration_user",
        is_staff=True,
        is_superuser=True,
        email="migration@example.com",
    )


def get_default_site():
    if settings.MIGRATION_DEFAULT_SITE_ID:
        return Site.objects.get(id=settings.MIGRATION_DEFAULT_SITE_ID)
    return Site.objects.get(id=1)
