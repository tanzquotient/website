# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0005_auto_20150304_1742'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='body_height',
            field=models.IntegerField(help_text=b"The user's body height in cm.", null=True, blank=True),
            preserve_default=True,
        ),
    ]
