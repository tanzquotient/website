# Generated by Django 2.2.11 on 2020-04-15 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0007_auto_20200413_1829'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='language',
            field=models.CharField(default='en', max_length=10),
        ),
    ]