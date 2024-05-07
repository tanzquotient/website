from django.db import migrations
from ..models import Event, EventCategory


def resize(apps, schema_editor):
    models = [Event, EventCategory]
    for model in models:
        instances_to_resize = model.objects.filter(image__isnull=False).all()
        for instance_to_resize in instances_to_resize:
            instance_to_resize.save(update_fields=["image"])


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0004_alter_event_image_alter_eventcategory_image"),
    ]

    operations = [
        migrations.RunPython(resize),
    ]
