from django.db import migrations


def resize(apps, schema_editor):
    Partner = apps.get_model("partners", "Partner")
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
