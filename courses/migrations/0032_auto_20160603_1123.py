# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0031_course_evaluated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursetype',
            name='name',
            field=models.CharField(unique=True, max_length=255),
        ),
    ]
