# Generated by Django 5.1.6 on 2025-03-20 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0047_alter_roomtranslation_disclaimer_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="coursetype",
            name="predecessors",
            field=models.ManyToManyField(
                blank=True,
                help_text="Course types that allow for early subscription (within time bounds) to courses if this type.",
                related_name="successors",
                to="courses.coursetype",
            ),
        ),
    ]
