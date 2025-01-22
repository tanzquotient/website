# Generated by Django 4.0.8 on 2023-01-06 19:34

import django.db.models.deletion
import parler.fields
import parler.models
from django.db import migrations, models
from djangocms_text.fields import HTMLField

import partners.models.partner


class Migration(migrations.Migration):
    replaces = [
        ("partners", "0001_initial"),
        ("partners", "0002_partner_active"),
        ("partners", "0003_alter_partner_image"),
    ]

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Partner",
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
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to=partners.models.partner.upload_path,
                        verbose_name="Image",
                    ),
                ),
                ("url", models.URLField()),
                ("active", models.BooleanField(default=True)),
            ],
            options={
                "abstract": False,
            },
            bases=(parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="PartnerTranslation",
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
                (
                    "language_code",
                    models.CharField(
                        db_index=True, max_length=15, verbose_name="Language"
                    ),
                ),
                ("name", models.CharField(max_length=100, verbose_name="Name")),
                (
                    "description",
                    HTMLField(blank=True, null=True, verbose_name="Description"),
                ),
                (
                    "master",
                    parler.fields.TranslationsForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="translations",
                        to="partners.partner",
                    ),
                ),
            ],
            options={
                "verbose_name": "partner Translation",
                "db_table": "partners_partner_translation",
                "db_tablespace": "",
                "managed": True,
                "default_permissions": (),
                "unique_together": {("language_code", "master")},
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
    ]
