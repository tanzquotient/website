# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0004_auto_20150319_1036'),
        ('courses', '0007_auto_20150319_1303'),
    ]

    operations = [
        migrations.CreateModel(
            name='MusicPluginModel',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('styles', models.ManyToManyField(help_text='Styles to be displayed in this plugin. Leave empty to show all styles.', to='courses.Style', null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
    ]
