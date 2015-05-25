# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import filer.fields.image


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0004_auto_20150326_1627'),
        ('filer', '0001_initial'),
        ('cms_plugins', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ThumbnailPluginModel',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('image', filer.fields.image.FilerImageField(blank=True, to='filer.Image', help_text='Image to show thumbnail for.', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
    ]
