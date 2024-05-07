from django.db import migrations
from ..models import UserProfile


def resize(apps, schema_editor):
    instances_to_resize = UserProfile.objects.filter(picture__isnull=False).all()
    for instance_to_resize in instances_to_resize:
        instance_to_resize.save(update_fields=["picture"])


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0027_alter_userprofile_picture"),
    ]

    operations = [
        migrations.RunPython(resize),
    ]
