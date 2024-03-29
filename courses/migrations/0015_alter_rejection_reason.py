# Generated by Django 4.2.6 on 2023-11-09 10:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0014_remove_course_evaluated_course_experience_mandatory"),
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
