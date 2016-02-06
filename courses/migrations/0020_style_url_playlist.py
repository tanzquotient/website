# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0019_auto_20151013_1222'),
    ]

    operations = [
        migrations.AddField(
            model_name='style',
            name='url_playlist',
            field=models.URLField(help_text=b'A url to a playlist (e.g on Spotify, Youtube).', max_length=500, null=True, blank=True),
        ),
    ]
