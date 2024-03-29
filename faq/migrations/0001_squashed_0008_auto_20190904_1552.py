# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-02-15 10:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import parler.fields


# Functions from the following migrations need manual copying.
# Move them and any dependencies into this file, then update the
# RunPython operations to refer to the local versions:
# faq.migrations.0004_auto_20160707_1251


def migrate_untranslated(apps, schema_editor):
    MyModel = apps.get_model("faq", "Question")
    MyModelTranslation = apps.get_model("faq", "QuestionTranslation")

    for object in MyModel.objects.all():
        MyModelTranslation.objects.create(
            master_id=object.pk,
            language_code="de",
            question_text=object.question_text,
            answer_text=object.answer_text,
        )


class Migration(migrations.Migration):
    replaces = [
        ("faq", "0001_initial"),
        ("faq", "0002_faqpluginmodel"),
        ("faq", "0003_auto_20160704_1158"),
        ("faq", "0004_auto_20160707_1251"),
        ("faq", "0005_auto_20160905_1307"),
        ("faq", "0006_auto_20170614_0757"),
        ("faq", "0007_auto_20170614_0929"),
        ("faq", "0008_auto_20190904_1552"),
    ]

    initial = True

    dependencies = [
        ("cms", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Question",
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
                ("question_text", models.TextField()),
                ("answer_text", models.TextField()),
                ("display", models.BooleanField(default=True)),
                (
                    "position",
                    models.PositiveSmallIntegerField(
                        default=0, verbose_name=b"Position"
                    ),
                ),
            ],
            options={
                "ordering": ["position"],
            },
        ),
        migrations.CreateModel(
            name="QuestionGroup",
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
                ("name", models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name="question",
            name="question_group",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="questions",
                to="faq.QuestionGroup",
            ),
        ),
        migrations.CreateModel(
            name="FaqPluginModel",
            fields=[
                (
                    "cmsplugin_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="cms.CMSPlugin",
                    ),
                ),
                (
                    "question_group",
                    models.ForeignKey(
                        help_text="Question group with questions to be displayed in this plugin.",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="faq.QuestionGroup",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("cms.cmsplugin",),
        ),
        migrations.AlterField(
            model_name="question",
            name="position",
            field=models.PositiveSmallIntegerField(default=0, verbose_name="Position"),
        ),
        migrations.CreateModel(
            name="QuestionTranslation",
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
                ("question_text", models.TextField(blank=True, null=True)),
                ("answer_text", models.TextField(blank=True, null=True)),
                (
                    "master",
                    models.ForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="translations",
                        to="faq.Question",
                    ),
                ),
            ],
            options={
                "db_tablespace": "",
                "default_permissions": (),
                "verbose_name": "question Translation",
                "db_table": "faq_question_translation",
                "managed": True,
            },
        ),
        migrations.AlterUniqueTogether(
            name="questiontranslation",
            unique_together=set([("language_code", "master")]),
        ),
        migrations.RunPython(
            code=migrate_untranslated,
        ),
        migrations.RemoveField(
            model_name="question",
            name="question_text",
        ),
        migrations.RemoveField(
            model_name="question",
            name="answer_text",
        ),
        migrations.AlterField(
            model_name="faqpluginmodel",
            name="cmsplugin_ptr",
            field=models.OneToOneField(
                auto_created=True,
                on_delete=django.db.models.deletion.CASCADE,
                parent_link=True,
                primary_key=True,
                related_name="faq_faqpluginmodel",
                serialize=False,
                to="cms.CMSPlugin",
            ),
        ),
        migrations.AlterField(
            model_name="question",
            name="question_group",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="questions",
                to="faq.QuestionGroup",
            ),
        ),
        migrations.AlterField(
            model_name="questiontranslation",
            name="answer_text",
            field=models.TextField(
                blank=True, null=True, verbose_name="[TR] Answer text"
            ),
        ),
        migrations.AlterField(
            model_name="questiontranslation",
            name="question_text",
            field=models.TextField(
                blank=True, null=True, verbose_name="[TR] Question text"
            ),
        ),
        migrations.AlterField(
            model_name="questiontranslation",
            name="master",
            field=parler.fields.TranslationsForeignKey(
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="translations",
                to="faq.Question",
            ),
        ),
    ]
