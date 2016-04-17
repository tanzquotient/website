# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0028_auto_20160415_1600'),
    ]

    operations = [
        migrations.AddField(
            model_name='rejection',
            name='mail_sent',
            field=models.BooleanField(default=True, help_text=b'If this rejection was communicated to user by email.'),
        ),
        migrations.AlterField(
            model_name='rejection',
            name='reason',
            field=models.CharField(default=b'unknown', max_length=30, choices=[(b'unknown', 'Unknown'), (b'overbooked', 'Overbooked'), (b'no_partner', 'No partner found'), (b'user_cancelled', 'User cancelled the subscription'), (b'illegitimate', 'Users subscription is illegitimate'), (b'banned', 'User is banned')]),
        ),
    ]
