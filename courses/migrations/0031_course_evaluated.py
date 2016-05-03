# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0030_auto_20160417_1743'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='evaluated',
            field=models.BooleanField(default=False, help_text=b'If this course was evaluated by a survey or another way.'),
        ),
    ]
