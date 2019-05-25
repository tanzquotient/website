# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0011_auto_20150522_1409'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='irregularlesson',
            options={'ordering': ['date', 'time_from']},
        ),
        migrations.AlterModelOptions(
            name='regularlessoncancellation',
            options={'ordering': ['date']},
        ),
    ]
