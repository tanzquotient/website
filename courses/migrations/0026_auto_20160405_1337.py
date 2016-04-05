# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0025_auto_20160405_1015'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscribe',
            name='matching_state',
            field=models.CharField(default=b'unknown', max_length=30, choices=[(b'unknown', 'Unknown'), (b'couple', 'Couple'), (b'to_match', 'To match'), (b'to_rematch', 'To rematch'), (b'matched', 'Matched'), (b'not_required', 'Not required')]),
        ),
    ]
