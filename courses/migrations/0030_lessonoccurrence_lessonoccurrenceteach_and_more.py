# Generated by Django 5.0.6 on 2024-06-03 22:14

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0029_alter_offeringtranslation_title"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="LessonOccurrence",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("start", models.DateTimeField()),
                ("end", models.DateTimeField()),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lesson_occurrences",
                        to="courses.course",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="LessonOccurrenceTeach",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "hourly_wage",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=6, null=True
                    ),
                ),
                (
                    "lesson_occurrence",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="courses.lessonoccurrence",
                    ),
                ),
                (
                    "teacher",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("lesson_occurrence", "teacher")},
            },
        ),
        migrations.AddField(
            model_name="lessonoccurrence",
            name="teachers",
            field=models.ManyToManyField(
                blank=True,
                null=True,
                related_name="lesson_occurrences",
                through="courses.LessonOccurrenceTeach",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterUniqueTogether(
            name="lessonoccurrence",
            unique_together={("course", "start", "end")},
        ),
    ]
