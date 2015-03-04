# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0004_auto_20150212_1504'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscribe',
            name='date',
            field=models.DateTimeField(help_text=b'The date/time when the subscription was made.', auto_now_add=True),
            preserve_default=True,
        ),
    ]
