from django.db import migrations
from ..models import Partner


def resize(apps, schema_editor):
    instances_to_resize = Partner.objects.filter(image__isnull=False).all()
    for instance_to_resize in instances_to_resize:
        instance_to_resize.save(update_fields=["image"])


class Migration(migrations.Migration):

    dependencies = [
        ("partners", "0002_alter_partner_image"),
    ]

    operations = [
        migrations.RunPython(resize),
    ]
