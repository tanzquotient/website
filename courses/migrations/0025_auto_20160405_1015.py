# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0024_subscribe_paymentmethod'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userprofile',
            options={'permissions': (('access_counterpayment', 'Can access counter payment'),)},
        ),
    ]
