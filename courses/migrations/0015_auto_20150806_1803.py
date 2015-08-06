# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0014_userprofile_get_involved'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='display',
            field=models.BooleanField(default=True, help_text=b'Defines if this course should be displayed on the Website (if checked, course is displayed if offering is displayed).'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='course',
            name='active',
            field=models.BooleanField(default=True, help_text=b'Defines if clients can subscribe to this course (if checked, course is active if offering is active).'),
            preserve_default=True,
        ),
    ]
