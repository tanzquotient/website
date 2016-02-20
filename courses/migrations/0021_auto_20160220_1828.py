# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0020_style_url_playlist'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='course',
            options={'ordering': ['position', 'type__name', 'name']},
        ),
        migrations.AlterField(
            model_name='style',
            name='url_playlist',
            field=models.URLField(help_text=b'A url to a playlist (e.g on online-Spotify, Youtube).', max_length=500, null=True, blank=True),
        ),
    ]
