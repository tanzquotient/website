# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0016_subscribe_matching_state'),
    ]

    operations = [
        migrations.RunSQL(
            r'''UPDATE courses_subscribe SET matching_state='couple' WHERE date >= DATE('2015-08-07') AND matching_state='unknown';'''
        ),
    ]
