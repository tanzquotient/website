from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("cms", "0021_auto_20180507_1432"),
    ]

    operations = [
        migrations.CreateModel(
            name="PageData",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title_id", models.CharField(max_length=50, verbose_name="title id")),
                ("language", models.CharField(max_length=15, verbose_name="language")),
                (
                    "creation_date",
                    models.DateTimeField(
                        blank=True,
                        editable=False,
                        null=True,
                        verbose_name="creation date",
                    ),
                ),
                ("published", models.BooleanField(blank=True)),
                ("publisher_is_draft", models.BooleanField()),
                ("publisher_state", models.SmallIntegerField()),
                (
                    "opposite_number_id",
                    models.CharField(
                        blank=True,
                        max_length=20,
                        null=True,
                        verbose_name="publisher public id",
                    ),
                ),
                ("page_id", models.CharField(max_length=50, verbose_name="page id")),
                (
                    "page_opposite_number_id",
                    models.CharField(
                        blank=True,
                        max_length=20,
                        null=True,
                        verbose_name="publisher public id",
                    ),
                ),
                ("page_publisher_is_draft", models.BooleanField()),
                ("path", models.CharField(max_length=255, verbose_name="path")),
            ],
        ),
        migrations.RunSQL(
            sql="drop index idx_100333_cms_page_node_id_publisher_is_draft_c1293d6a_uniq"
        ),
        migrations.RunSQL(
            sql="""
            alter table cms_page
                add constraint idx_100333_cms_page_node_id_publisher_is_draft_c1293d6a_uniq
                    unique (node_id, publisher_is_draft);
        """
        ),
        migrations.RunSQL(
            sql="drop index idx_100384_cms_title_language_7a69dc7eaf856287_uniq"
        ),
        migrations.RunSQL(
            sql="""
            alter table cms_title
                add constraint idx_100384_cms_title_language_7a69dc7eaf856287_uniq  unique (id, language, title)
            """
        ),
        migrations.RunSQL(
            sql="""
            alter table cms_title
                add constraint idx_100384_cms_language_page_id_7a69dc7eaf856287_uniq
                    unique (language, page_id);
            """
        ),
    ]
