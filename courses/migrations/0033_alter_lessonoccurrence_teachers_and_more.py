# Generated by Django 5.0.6 on 2024-06-04 15:00

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0032_remove_teach_hourly_wage"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="lessonoccurrence",
            name="teachers",
            field=models.ManyToManyField(
                blank=True,
                related_name="lesson_occurrences",
                through="courses.LessonOccurrenceTeach",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="lessonoccurrenceteach",
            name="hourly_wage",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=6),
            preserve_default=False,
        ),
    ]
