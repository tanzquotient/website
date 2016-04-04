# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0023_auto_20160403_1754'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscribe',
            name='paymentmethod',
            field=models.CharField(blank=True, max_length=30, null=True, choices=[(b'counter', 'counter'), (b'course', 'course'), (b'online', 'online'), (b'voucher', 'voucher')]),
        ),
    ]
