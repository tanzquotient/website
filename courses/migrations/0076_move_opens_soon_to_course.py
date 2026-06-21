from django.db import migrations, models


def migrate_opens_soon(apps, schema_editor):
    Offering = apps.get_model("courses", "Offering")
    for offering in Offering.objects.filter(opens_soon=True):
        offering.course_set.update(opens_soon=True)


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0075_alter_coursetranslation_unique_together_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="course",
            name="opens_soon",
            field=models.BooleanField(
                default=False,
                help_text='If set to true, the sign up page says "opens soon" instead of "closed"',
            ),
        ),
        migrations.RunPython(migrate_opens_soon, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="offering",
            name="opens_soon",
        ),
    ]
