# Generated by Django 4.2.4 on 2023-10-01 12:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0011_alter_bankaccount_iban_alter_userprofile_address_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="offering",
            name="order",
            field=models.PositiveSmallIntegerField(
                default=10,
                help_text="Defines how offerings are ordered on the course page. The lower the number, the further on top.",
            ),
        ),
        migrations.AlterField(
            model_name="offering",
            name="limit_courses_per_section",
            field=models.PositiveSmallIntegerField(
                blank=True,
                help_text="If set, only that many courses are shown for each section of the course list. The remaining courses will be shown when expanding the section.",
                null=True,
            ),
        ),
    ]
