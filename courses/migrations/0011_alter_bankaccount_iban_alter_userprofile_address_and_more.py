# Generated by Django 4.2.1 on 2023-08-06 18:38

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


def delete_empty_bank_accounts(apps, schema_editor):
    for profile in apps.get_model("courses", "UserProfile").objects.all():
        if profile.bank_account and not profile.bank_account.iban:
            profile.bank_account = None
            profile.save()

    apps.get_model("courses", "BankAccount").objects.filter(
        user_profile__isnull=True
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0010_alter_teach_hourly_wage_delete_teachlesson"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bankaccount",
            name="iban",
            field=models.CharField(
                help_text="IBAN in the standardized format.",
                max_length=255,
                validators=[django.core.validators.MinLengthValidator(1)],
            ),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="address",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="courses.address",
            ),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="bank_account",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="user_profile",
                to="courses.bankaccount",
            ),
        ),
        migrations.RunPython(delete_empty_bank_accounts),
    ]
