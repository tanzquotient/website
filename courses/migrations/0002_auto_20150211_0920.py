# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coursetype',
            name='special',
        ),
        migrations.AddField(
            model_name='course',
            name='active',
            field=models.BooleanField(default=True, help_text=b'Defines if clients can subscribe to this course (if false, value is inherited from offering).'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='course',
            name='special',
            field=models.TextField(help_text=b'Any special properties of this course.', null=True, blank=True),
            preserve_default=True,
        ),
    ]
