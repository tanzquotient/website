from django.db import migrations
from datetime import timedelta


def resize(apps, schema_editor):
    SurveyInstance = apps.get_model("survey", "SurveyInstance")
    instances_to_update = SurveyInstance.objects.filter(
        url_expire_date__isnull=True
    ).all()
    for instance_to_update in instances_to_update:
        instance_to_update.url_expire_date = instance_to_update.date + timedelta(
            days=90
        )
        instance_to_update.save(update_fields=["url_expire_date"])


class Migration(migrations.Migration):

    dependencies = [
        ("survey", "0004_remove_surveyinstance_invitation_sent"),
    ]

    operations = [
        migrations.RunPython(resize),
    ]
