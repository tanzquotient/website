# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0004_auto_20160504_0949'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='surveyinstance',
            name='url_checksum',
        ),
        migrations.RemoveField(
            model_name='surveyinstance',
            name='url_text',
        ),
    ]
