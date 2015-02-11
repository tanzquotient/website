# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_auto_20150211_0920'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='active',
            field=models.BooleanField(default=True, help_text=b'Defines if clients can subscribe to this course (if unchecked, course is active if offering is active).'),
            preserve_default=True,
        ),
    ]
