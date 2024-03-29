# Generated by Django 4.2.6 on 2023-10-15 19:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("payment", "0002_squashed"),
    ]

    operations = [
        migrations.AlterField(
            model_name="financefile",
            name="type",
            field=models.CharField(
                choices=[
                    ("postfinance_xml", "Postfinance XML"),
                    ("zkb_csv", "ZKB CSV"),
                ],
                default="zkb_csv",
                max_length=32,
            ),
        ),
    ]
