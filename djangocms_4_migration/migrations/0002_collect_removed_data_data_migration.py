from django.db import migrations


def forwards(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Title = apps.get_model("cms", "Title")
    PageData = apps.get_model("djangocms_4_migration", "PageData")

    # Get all titles, Ordered by id descending to ensure that drafts are provided first. Check this doc
    for title in Title.objects.using(db_alias).order_by('-id').all():
        PageData(
            title_id=title.pk,
            language=title.language,
            published=title.published,
            publisher_is_draft=title.publisher_is_draft,
            publisher_state=title.publisher_state,
            creation_date=title.creation_date,
            opposite_number_id=title.publisher_public_id,
            page_id=title.page.pk,
            page_opposite_number_id=title.page.publisher_public_id,
            page_publisher_is_draft=title.page.publisher_is_draft,
            path=title.path,
        ).save()


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_4_migration', '0001_initial'),
    ]

    run_before = [
        ('cms', '0023_placeholder_source_field'),  # Be sure to run before CMS 4.0 migrations. After all 3.5 have run.
    ]

    operations = [
        migrations.RunPython(forwards),
    ]
