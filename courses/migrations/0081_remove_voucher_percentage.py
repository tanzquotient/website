from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0080_remove_voucher_percentage"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="voucher",
            constraint=models.CheckConstraint(
                condition=models.Q(("amount__isnull", False), ("amount__gt", 0)),
                name="amount is non-null and positive",
            ),
        ),
        migrations.RemoveField(
            model_name="voucher",
            name="percentage",
        ),
    ]
