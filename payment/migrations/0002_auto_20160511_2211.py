# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='transaction_id',
            field=models.CharField(max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='payment',
            name='iban',
            field=models.CharField(max_length=34, null=True, blank=True),
        ),
    ]
