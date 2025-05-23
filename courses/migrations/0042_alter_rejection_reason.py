# Generated by Django 5.0.9 on 2024-12-09 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0041_userprofile_display_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="rejection",
            name="reason",
            field=models.CharField(
                choices=[
                    ("unknown", "Unknown"),
                    (
                        "requirements_not_met",
                        "User and/or partner does not meet requirements",
                    ),
                    ("overbooked", "Overbooked"),
                    ("no_partner", "No partner found"),
                    ("user_cancelled", "User cancelled the subscription"),
                    ("illegitimate", "Users subscription is illegitimate"),
                    ("banned", "User is banned"),
                    ("course_cancelled", "Course was cancelled"),
                ],
                default="unknown",
                max_length=30,
            ),
        ),
    ]
