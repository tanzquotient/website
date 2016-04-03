# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import courses.models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0022_auto_20160401_2320'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscribe',
            name='usi',
            field=models.CharField(default=b'------', help_text='Unique subscription identifier: 4 characters identifier, 2 characters checksum', unique=True, max_length=6, blank=True),
        ),
        migrations.AlterField(
            model_name='voucher',
            name='key',
            field=models.CharField(default=courses.models.generate_key, unique=True, max_length=8),
        ),
    ]
