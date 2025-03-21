# Generated by Django 5.1.6 on 2025-02-16 21:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0047_alter_roomtranslation_disclaimer_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="song",
            name="style",
        ),
        migrations.AlterField(
            model_name="coursetype",
            name="predecessors",
            field=models.ManyToManyField(
                blank=True,
                help_text="Course types that allow for early subscription (within time "
                "bounds) to courses if this type.",
                related_name="successors",
                to="courses.coursetype",
            ),
        ),
        migrations.DeleteModel(
            name="MusicPluginModel",
        ),
        migrations.DeleteModel(
            name="Song",
        ),
    ]
