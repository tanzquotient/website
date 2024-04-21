# Generated by Django 5.0.3 on 2024-04-21 17:02

import djangocms_text_ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0019_offering_survey_alter_voucher_sent_to"),
    ]

    operations = [
        migrations.AddField(
            model_name="coursetranslation",
            name="information_for_participants",
            field=djangocms_text_ckeditor.fields.HTMLField(
                blank=True,
                help_text="Shown only to participants of the course on course page. Can be set by teachers in the frontend.",
                null=True,
                verbose_name="[TR] Information for participants",
            ),
        ),
    ]
