# Generated by Django 5.0.9 on 2024-11-24 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("survey", "0005_survey_instance_default_expiration_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="surveyinstance",
            name="url_expire_date",
            field=models.DateTimeField(),
        ),
    ]
