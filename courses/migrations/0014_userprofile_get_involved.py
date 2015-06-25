# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0013_auto_20150616_1102'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='get_involved',
            field=models.BooleanField(default=False, help_text=b'If this user is interested to get involved with our organisation.'),
            preserve_default=True,
        ),
    ]
