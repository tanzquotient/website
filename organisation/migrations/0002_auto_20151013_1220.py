# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organisation', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='function',
            name='email',
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
    ]
