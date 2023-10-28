# Generated by Django 4.2.4 on 2023-09-21 19:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("events", "0002_squashed"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="eventcategory",
            options={"ordering": ["position"]},
        ),
        migrations.AddField(
            model_name="eventcategory",
            name="position",
            field=models.PositiveSmallIntegerField(default=0, verbose_name="Position"),
        ),
    ]