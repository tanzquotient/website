# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0001_initial'),
        ('djangocms_link', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ButtonPluginModel',
            fields=[
                ('link_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='djangocms_link.Link')),
                ('emphasize', models.BooleanField(default=False, help_text='If this button should be visually emphasized.')),
            ],
            options={
                'abstract': False,
            },
            bases=('djangocms_link.link',),
        ),
        migrations.CreateModel(
            name='PageTitlePluginModel',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('title', models.CharField(help_text="The title to be displayed. Leave empty to display the page's title.", max_length=30, null=True, blank=True)),
                ('subtitle', models.CharField(help_text='The subtitle to be displayed.', max_length=50, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
    ]
