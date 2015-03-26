# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import filer.fields.image


class Migration(migrations.Migration):

    dependencies = [
        ('filer', '0001_initial'),
        ('events', '0004_eventsteaserpluginmodel'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='comment',
        ),
        migrations.AddField(
            model_name='event',
            name='image',
            field=filer.fields.image.FilerImageField(blank=True, to='filer.Image', help_text='Advertising image for this event.', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='price_special',
            field=models.CharField(help_text='Set this only if you want a different price schema.', max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
    ]
