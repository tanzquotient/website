from django.db import migrations, models


def delete_invalid_vouchers(apps, schema_editor):
    Voucher = apps.get_model("courses", "Voucher")
    Voucher.objects.filter(
        models.Q(amount__isnull=True) | models.Q(amount__lte=0)
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        (
            "courses",
            "0079_remove_voucher_percentage_is_null_or_between_0_and_100_and_more",
        ),
    ]

    operations = [
        migrations.RunPython(delete_invalid_vouchers, migrations.RunPython.noop),
    ]
