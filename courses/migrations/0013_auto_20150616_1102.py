# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import userena.models
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0012_auto_20150525_1844'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userprofile',
            options={'permissions': (('view_profile', 'Can view profile'),)},
        ),
        migrations.AddField(
            model_name='userprofile',
            name='language',
            field=models.CharField(default=b'de', help_text='Default language.', max_length=5, verbose_name='language', choices=[(b'de', b'Deutsch'), (b'en', b'English')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='mugshot',
            field=easy_thumbnails.fields.ThumbnailerImageField(help_text='A personal image displayed in your profile.', upload_to=userena.models.upload_to_mugshot, verbose_name='mugshot', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='privacy',
            field=models.CharField(default=b'registered', help_text='Designates who can view your profile.', max_length=15, verbose_name='privacy', choices=[(b'open', 'Open'), (b'registered', 'Registered'), (b'closed', 'Closed')]),
            preserve_default=True,
        ),
    ]
