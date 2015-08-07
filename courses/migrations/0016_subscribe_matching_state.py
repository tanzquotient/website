# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0015_auto_20150806_1803'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscribe',
            name='matching_state',
            field=models.CharField(default=b'unknown', max_length=30, choices=[(b'unknown', 'Unknown'), (b'couple', 'Couple'), (b'to_match', 'To match'), (b'matched', 'Matched'), (b'not_required', 'Not required')]),
            preserve_default=True,
        ),
    ]
