# Generated by Django 2.2.11 on 2020-04-01 12:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0005_auto_20200331_1936'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='bank_account',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_profile', to='courses.BankAccount'),
        ),
    ]
