# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='display',
            field=models.BooleanField(default=True, help_text=b'Defines if this event should be displayed on the website.'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='price_without_legi',
            field=models.FloatField(help_text=b'Leave this empty for free entrance', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='special',
            field=models.BooleanField(default=False, help_text=b'If this is a special event that should be emphasized on the website'),
            preserve_default=True,
        ),
    ]
