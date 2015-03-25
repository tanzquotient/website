# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0001_initial'),
        ('events', '0003_auto_20150319_1303'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventsTeaserPluginModel',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('delta_days', models.IntegerField(help_text='Events within the time delta (in days) from now on are shown. Leave empty to make no restrictions.', null=True, blank=True)),
                ('max_displayed', models.IntegerField(help_text='Maximum number of events to be displayed. Leave empty to make no restrictions.', null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
    ]
